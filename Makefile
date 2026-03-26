# pyArgos Makefile
# Usage: make <target>

.PHONY: help \
        mermaid-pull render-diagrams render-diagrams-force \
        docs-deps docs-build docs-build-strict docs-serve docs-deploy docs-clean

help:
	@echo "pyArgos targets:"
	@echo ""
	@echo "  Documentation:"
	@echo "    make docs-build          Build full site (render diagrams + mkdocs build)"
	@echo "    make docs-serve          Start local MkDocs preview server"
	@echo "    make docs-deploy         Deploy to GitHub Pages"
	@echo "    make docs-clean          Remove built site/"
	@echo "    make render-diagrams     Render new/changed Mermaid diagrams to SVG"
	@echo "    make render-diagrams-force  Re-render ALL diagrams"
	@echo "    make mermaid-pull        Pull the mermaid-cli Docker image"
	@echo "    make docs-deps           Install documentation dependencies"

# --- Documentation ---

mermaid-pull:
	@echo "Pulling mermaid-cli Docker image..."
	docker pull minlag/mermaid-cli
	@echo "Done. Run 'make render-diagrams' to render all Mermaid diagrams."

render-diagrams: mermaid-pull
	@echo "Rendering Mermaid diagrams to SVG (skips unchanged)..."
	python render_diagrams.py
	@echo "Done. SVGs saved to docs/images/diagrams/"

render-diagrams-force: mermaid-pull
	@echo "Re-rendering ALL Mermaid diagrams to SVG..."
	python render_diagrams.py --force
	@echo "Done. All SVGs regenerated."

docs-deps:
	@echo "Installing documentation dependencies..."
	pip install mkdocs-material mkdocstrings mkdocstrings-python
	@echo "Done."

docs-build: render-diagrams
	@echo "Building MkDocs site..."
	mkdocs build
	@echo "Done. Static site built in site/"

docs-build-strict: render-diagrams
	@echo "Building MkDocs site (strict mode)..."
	mkdocs build --strict
	@echo "Done. Static site built in site/"

docs-serve: render-diagrams
	@echo "Starting MkDocs development server at http://127.0.0.1:8000"
	./serve_docs.sh

docs-deploy: render-diagrams
	@echo "Deploying documentation to GitHub Pages..."
	mkdocs gh-deploy --force
	@echo "Done. Site deployed."

docs-clean:
	@echo "Removing built site..."
	rm -rf site/
	@echo "Done."
