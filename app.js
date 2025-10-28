// Utrecht Open Data Frontend Application

class UtrechtOpenDataApp {
  constructor() {
    this.apiBaseUrl = "/api"; // Gebruik lokale proxy
    this.currentResults = [];

    this.initializeElements();
    this.attachEventListeners();
    this.loadInitialData();
  }

  initializeElements() {
    this.searchInput = document.getElementById("searchInput");
    this.searchButton = document.getElementById("searchButton");
    this.clearButton = document.getElementById("clearButton");
    this.limitSelect = document.getElementById("limitSelect");
    this.statusMessage = document.getElementById("statusMessage");
    this.resultsCount = document.getElementById("resultsCount");
    this.resultsContainer = document.getElementById("resultsContainer");
    this.detailsSection = document.getElementById("detailsSection");
    this.detailsContainer = document.getElementById("detailsContainer");
    this.closeDetailsButton = document.getElementById("closeDetails");
  }

  attachEventListeners() {
    this.searchButton.addEventListener("click", () => this.performSearch());
    this.clearButton.addEventListener("click", () => this.clearSearch());
    this.closeDetailsButton.addEventListener("click", () =>
      this.closeDetails(),
    );

    this.searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.performSearch();
      }
    });
  }

  // Helper functie om attributen op te halen met namespace ondersteuning
  getAttr(attributes, key) {
    // De API gebruikt namespaced attributen zoals "dct:title"
    if (attributes[`dct:${key}`]) return attributes[`dct:${key}`];
    if (attributes[`dcat:${key}`]) return attributes[`dcat:${key}`];
    if (attributes[`foaf:${key}`]) return attributes[`foaf:${key}`];
    if (attributes[key]) return attributes[key];
    return null;
  }

  async loadInitialData() {
    this.showStatus("Datasets laden...", "loading");
    await this.performSearch();
  }

  async performSearch() {
    const query = this.searchInput.value.trim();
    const limit = parseInt(this.limitSelect.value);

    this.showStatus("Zoeken...", "loading");

    try {
      const datasets = await this.fetchDatasets(limit);

      if (datasets.length === 0) {
        this.showStatus("Geen datasets gevonden", "info");
        this.currentResults = [];
        this.renderResults([]);
        return;
      }

      // Filter op query indien opgegeven
      let filteredDatasets = datasets;
      if (query) {
        filteredDatasets = this.filterDatasets(datasets, query);

        if (filteredDatasets.length === 0) {
          this.showStatus(`Geen resultaten gevonden voor "${query}"`, "info");
          this.renderResults([]);
          return;
        }
      }

      this.currentResults = filteredDatasets;
      this.renderResults(filteredDatasets);

      if (query) {
        this.showStatus(
          `${filteredDatasets.length} resultaten gevonden voor "${query}"`,
          "success",
        );
      } else {
        this.showStatus(
          `${filteredDatasets.length} datasets geladen`,
          "success",
        );
      }
    } catch (error) {
      console.error("Fout bij zoeken:", error);
      this.showStatus(`Fout bij ophalen van data: ${error.message}`, "error");
      this.renderResults([]);
    }
  }

  async fetchDatasets(limit = 20) {
    const url = `${this.apiBaseUrl}/datasets?start=0`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("API Response:", data); // Debug logging
    return data.data || [];
  }

  filterDatasets(datasets, query) {
    const queryLower = query.toLowerCase();

    return datasets.filter((dataset) => {
      const attributes = dataset.attributes || {};
      const title = (this.getAttr(attributes, "title") || "").toLowerCase();
      const description = (
        this.getAttr(attributes, "description") || ""
      ).toLowerCase();
      const keywords = this.getAttr(attributes, "keyword") || [];
      const keywordsStr = (
        Array.isArray(keywords) ? keywords.join(" ") : ""
      ).toLowerCase();
      const id = (dataset.id || "").toLowerCase();

      return (
        title.includes(queryLower) ||
        description.includes(queryLower) ||
        keywordsStr.includes(queryLower) ||
        id.includes(queryLower)
      );
    });
  }

  renderResults(datasets) {
    this.resultsCount.textContent =
      datasets.length > 0
        ? `${datasets.length} dataset${datasets.length !== 1 ? "s" : ""} gevonden`
        : "";

    if (datasets.length === 0) {
      this.resultsContainer.innerHTML =
        '<div class="no-results">Geen datasets gevonden</div>';
      return;
    }

    const html = datasets
      .map((dataset) => this.createDatasetCard(dataset))
      .join("");
    this.resultsContainer.innerHTML = html;

    // Voeg event listeners toe aan knoppen
    datasets.forEach((dataset) => {
      const card = document.getElementById(`dataset-${dataset.id}`);
      if (card) {
        card.addEventListener("click", () =>
          this.showDatasetDetails(dataset.id),
        );
      }
    });
  }

  createDatasetCard(dataset) {
    const attributes = dataset.attributes || {};
    const title = this.escapeHtml(
      this.getAttr(attributes, "title") || dataset.id || "Geen titel",
    );
    const description = this.escapeHtml(
      this.getAttr(attributes, "description") ||
        "Geen beschrijving beschikbaar",
    );
    const truncatedDescription =
      description.length > 200
        ? description.substring(0, 200) + "..."
        : description;

    const keywords = this.getAttr(attributes, "keyword") || [];
    const keywordTags = (Array.isArray(keywords) ? keywords.slice(0, 5) : [])
      .map((kw) => `<span class="tag">${this.escapeHtml(kw)}</span>`)
      .join("");

    const modified = this.getAttr(attributes, "modified");
    const modifiedDate = modified
      ? new Date(modified).toLocaleDateString("nl-NL")
      : "";

    return `
            <div class="dataset-card" id="dataset-${dataset.id}">
                <div class="dataset-header">
                    <h3 class="dataset-title">${title}</h3>
                    ${modifiedDate ? `<span class="dataset-date">Bijgewerkt: ${modifiedDate}</span>` : ""}
                </div>
                <p class="dataset-description">${truncatedDescription}</p>
                ${keywordTags ? `<div class="dataset-keywords">${keywordTags}</div>` : ""}
                <div class="dataset-footer">
                    <span class="dataset-id">ID: ${this.escapeHtml(dataset.id)}</span>
                    <button class="view-details-btn" data-id="${dataset.id}">
                        Details bekijken →
                    </button>
                </div>
            </div>
        `;
  }

  async showDatasetDetails(datasetId) {
    this.showStatus("Dataset details laden...", "loading");

    try {
      const dataset = await this.fetchDatasetDetails(datasetId);
      const distributions = await this.fetchDistributions(datasetId);

      this.renderDatasetDetails(dataset, distributions);
      this.detailsSection.classList.remove("hidden");
      this.showStatus("", "success");

      // Scroll naar details
      this.detailsSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    } catch (error) {
      console.error("Fout bij ophalen dataset details:", error);
      this.showStatus(
        `Fout bij ophalen van dataset details: ${error.message}`,
        "error",
      );
    }
  }

  async fetchDatasetDetails(datasetId) {
    const url = `${this.apiBaseUrl}/datasets/${datasetId}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Dataset details:", data); // Debug logging
    return data.data || data;
  }

  async fetchDistributions(datasetId) {
    const url = `${this.apiBaseUrl}/datasets/${datasetId}/distributions`;

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        console.warn("Geen distributies beschikbaar");
        return [];
      }

      const data = await response.json();
      console.log("Distributions:", data); // Debug logging
      return data.data || [];
    } catch (error) {
      console.error("Fout bij ophalen distributies:", error);
      return [];
    }
  }

  renderDatasetDetails(dataset, distributions) {
    const attributes = dataset.attributes || {};

    const title = this.escapeHtml(
      this.getAttr(attributes, "title") || dataset.id || "Geen titel",
    );
    const description = this.escapeHtml(
      this.getAttr(attributes, "description") ||
        "Geen beschrijving beschikbaar",
    );
    const id = this.escapeHtml(dataset.id);

    const keywords = this.getAttr(attributes, "keyword") || [];
    const keywordTags = (Array.isArray(keywords) ? keywords : [])
      .map((kw) => `<span class="tag">${this.escapeHtml(kw)}</span>`)
      .join("");

    const issued = this.getAttr(attributes, "issued");
    const issuedDate = issued
      ? new Date(issued).toLocaleDateString("nl-NL", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      : "Onbekend";

    const modified = this.getAttr(attributes, "modified");
    const modifiedDate = modified
      ? new Date(modified).toLocaleDateString("nl-NL", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      : "Onbekend";

    const publisher = this.getAttr(attributes, "publisher");
    const publisherName = publisher
      ? typeof publisher === "object"
        ? publisher.name || this.getAttr(publisher, "name") || "Onbekend"
        : publisher
      : "Onbekend";

    const license = this.getAttr(attributes, "license");
    const licenseName = license
      ? typeof license === "string"
        ? license
        : license.name || this.getAttr(license, "name") || "Onbekend"
      : "Onbekend";

    let distributionsHtml = "<p>Geen distributies beschikbaar</p>";
    if (distributions.length > 0) {
      distributionsHtml = distributions
        .map((dist) => {
          const distAttrs = dist.attributes || {};
          const format = this.escapeHtml(
            this.getAttr(distAttrs, "format") || "Onbekend",
          );
          const distTitle = this.escapeHtml(
            this.getAttr(distAttrs, "title") || format,
          );
          const accessURL = this.getAttr(distAttrs, "accessURL") || "";
          const mediaType = this.getAttr(distAttrs, "mediaType") || "";
          const byteSize = this.getAttr(distAttrs, "byteSize");

          let sizeText = "";
          if (byteSize) {
            const sizeMB = (byteSize / (1024 * 1024)).toFixed(2);
            sizeText = `${sizeMB} MB`;
          }

          return `
                    <div class="distribution-item">
                        <div class="distribution-header">
                            <span class="distribution-format">${format}</span>
                            ${sizeText ? `<span class="distribution-size">${sizeText}</span>` : ""}
                        </div>
                        <div class="distribution-title">${distTitle}</div>
                        ${mediaType ? `<div class="distribution-meta">Type: ${this.escapeHtml(mediaType)}</div>` : ""}
                        ${
                          accessURL
                            ? `
                            <a href="${this.escapeHtml(accessURL)}"
                               target="_blank"
                               class="download-button">
                                Download ${format} ↓
                            </a>
                        `
                            : ""
                        }
                    </div>
                `;
        })
        .join("");
    }

    const html = `
            <div class="details-content">
                <h2>${title}</h2>

                <div class="details-meta">
                    <div class="meta-item">
                        <strong>Dataset ID:</strong> ${id}
                    </div>
                    <div class="meta-item">
                        <strong>Uitgever:</strong> ${this.escapeHtml(publisherName)}
                    </div>
                    <div class="meta-item">
                        <strong>Gepubliceerd:</strong> ${issuedDate}
                    </div>
                    <div class="meta-item">
                        <strong>Laatst gewijzigd:</strong> ${modifiedDate}
                    </div>
                    <div class="meta-item">
                        <strong>Licentie:</strong> ${this.escapeHtml(licenseName)}
                    </div>
                </div>

                <div class="details-section-block">
                    <h3>Beschrijving</h3>
                    <p>${description}</p>
                </div>

                ${
                  keywords.length > 0
                    ? `
                    <div class="details-section-block">
                        <h3>Trefwoorden</h3>
                        <div class="dataset-keywords">${keywordTags}</div>
                    </div>
                `
                    : ""
                }

                <div class="details-section-block">
                    <h3>Beschikbare formaten</h3>
                    <div class="distributions-list">
                        ${distributionsHtml}
                    </div>
                </div>
            </div>
        `;

    this.detailsContainer.innerHTML = html;
  }

  closeDetails() {
    this.detailsSection.classList.add("hidden");
  }

  clearSearch() {
    this.searchInput.value = "";
    this.searchInput.focus();
    this.performSearch();
  }

  showStatus(message, type = "info") {
    this.statusMessage.textContent = message;
    this.statusMessage.className = `status-message ${type}`;

    if (type === "success" && message) {
      setTimeout(() => {
        this.statusMessage.textContent = "";
        this.statusMessage.className = "status-message";
      }, 3000);
    }
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialiseer de applicatie wanneer de pagina geladen is
document.addEventListener("DOMContentLoaded", () => {
  new UtrechtOpenDataApp();
});
