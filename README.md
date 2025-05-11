# Home Slice

Real estate market insights application providing weekly housing metrics and market analysis.

## Project Structure

- `data-service/`: Python scripts for data ingestion and processing
- `api/`: FastAPI backend service
- `frontend/`: React + Vite frontend application

## Development Setup

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Set up Python environment:

   ```bash
   cd data-service
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start development servers:
   ```bash
   pnpm dev
   ```

## Data Sources

- Redfin Data Center
- FRED (Federal Reserve Economic Data)

## License

MIT
