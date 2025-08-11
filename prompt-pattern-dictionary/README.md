# Prompt Pattern Dictionary

A comprehensive, searchable dictionary of prompt engineering patterns for cybersecurity applications. This project provides an OED-style interface for discovering and learning prompt patterns extracted from research papers.

## 🎯 Project Overview

This is a Next.js-based web application that transforms academic research on prompt engineering into an accessible, searchable dictionary. It serves as the definitive reference tool for cybersecurity prompt engineering patterns.

For the normalized Prompt Pattern schema and mapping details, see the Product Requirements Document (Prompt Pattern Schema section): docs/PRD.md.

### Key Features

- **Dictionary-Style Interface**: Clean, professional layout inspired by the Oxford English Dictionary
- **Advanced Search**: Full-text search with category filtering and fuzzy matching
- **Research Paper Integration**: Direct links to source papers with proper attribution
- **Pattern Categories**: Organized by Input Semantics, Output Customization, Security Testing, etc.
- **Copy-to-Clipboard**: Easy copying of prompt examples
- **Responsive Design**: Optimized for desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/timhaintz/PromptEngineering4Cybersecurity.git

# Navigate to the project
cd PromptEngineering4Cybersecurity/prompt-pattern-dictionary

# Install dependencies
npm install

# Process the source data
npm run build-data

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dictionary.

## 📁 Project Structure

```
prompt-pattern-dictionary/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable React components
│   ├── lib/             # Utilities and data processing
│   └── types/           # TypeScript definitions
├── public/
│   └── data/            # Processed pattern data
├── scripts/             # Build and data processing scripts
└── docs/                # Project documentation
```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build-data` - Process source JSON into optimized format
- `npm run lint` - Run ESLint
- `npm test` - Run tests

### Data Processing

The application processes `../promptpatterns.json` to create:
- Individual pattern pages
- Search indexes
- Category listings
- Cross-references

## 📚 Documentation

- [Product Requirements Document](docs/PRD.md)
- [Folder Structure Guide](docs/FOLDER_STRUCTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🌐 Deployment

This project is configured for deployment to GitHub Pages:

```bash
npm run build
npm run export
```

The static files will be generated in the `out/` directory, ready for GitHub Pages hosting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Research papers and authors whose work is cataloged in this dictionary
- The prompt engineering and cybersecurity communities
- Contributors to the open-source ecosystem

## 📞 Support

For questions or support, please open an issue in the GitHub repository.
