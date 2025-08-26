# Dynamic Elements Manager

A sophisticated full-stack AI application that enables users to configure, validate, and deploy dynamic AI-powered elements for data analysis and extraction tasks. The system provides an end-to-end workflow from configuration through production deployment with comprehensive testing and calibration capabilities.

## 🎯 Overview

Dynamic Elements Manager streamlines the process of creating and managing AI-powered data processing pipelines. Users can configure custom AI elements with specific prompts, validate them with real data, and build calibration datasets for consistent production performance.

### Key Capabilities
- **🤖 AI-Powered Analysis**: Support for GPT-4, Claude 3, and Gemini Pro models
- **📊 Dual Analysis Methods**: RAG-based reasoning and autonomous script generation
- **🔧 Visual Configuration**: Intuitive web interface for element configuration
- **✅ Validation Pipeline**: Test and validate elements before production use
- **📈 Calibration System**: Build datasets and run consistency testing
- **📁 Multi-Format Support**: Handle TXT, PDF, DOCX, CSV, and custom formats
- **🧪 Comprehensive Testing**: End-to-end testing with Playwright

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Next.js 14 + React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **AI Integration**: OpenAI GPT-4o, text-embedding-ada-002
- **Testing**: Playwright E2E testing framework
- **UI Components**: Radix UI with custom styling

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Services   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (OpenAI)      │
│                 │    │                 │    │                 │
│ • React UI      │    │ • REST API      │    │ • GPT-4o        │
│ • TypeScript    │    │ • SQLAlchemy    │    │ • Embeddings    │
│ • Tailwind      │    │ • File Upload   │    │ • Analysis      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       │                 │
                       │ • Elements      │
                       │ • Dataset       │
                       │ • Files         │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ for frontend
- **Python** 3.8+ for backend
- **Git** for version control

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd dynamic-elements-manager

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Environment Configuration

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Backend (.env):**
```env
DATABASE_URL=sqlite:///./dynamic_elements.db
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=52428800
ALLOWED_EXTENSIONS=txt,pdf,docx,csv,ppr-rx,ppr-vx
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Application
```bash
# Terminal 1: Start Backend (Port 8000)
cd backend
python run.py

# Terminal 2: Start Frontend (Port 3000)
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔄 User Workflow

The Dynamic Elements Manager follows a three-stage workflow:

### Stage 1: Configuration 🔧
**Purpose**: Create and configure AI-powered elements

1. **Access Configuration**: Click "Configure Element" on the homepage
2. **Define AI Prompt**: Write specific instructions for the AI analysis task
3. **Select AI Model**: Choose from GPT-4, GPT-3.5, Claude 3, or Gemini Pro
4. **Choose Method**:
   - **Reasoning**: RAG-based analysis with document search
   - **Extraction**: Autonomous Python script generation
5. **Set File Types**: Select supported file formats (TXT, PDF, DOCX, CSV, etc.)
6. **Configure Data Sources**: Choose from KPI tables, DE, or other data sources
7. **Save Element**: Name and save the configuration for testing

### Stage 2: Validation ✅
**Purpose**: Test and validate elements with real data

1. **Access Dashboard**: Click "View Dashboard" to see all elements
2. **Upload Test Files**: Add real files matching your element's configuration
3. **Run Analysis**: Execute AI analysis with uploaded files
4. **Review Results**: Examine AI output for accuracy and relevance
5. **Validate Element**: Mark as "validated" if results meet quality standards
6. **Build Dataset**: Add successful results to calibration dataset
7. **Iterate**: Edit configuration if results need improvement

### Stage 3: Calibration & Testing 📊
**Purpose**: Perform end-to-end testing with calibration datasets

1. **Access Testing Suite**: Click "Open Testing Suite" on homepage
2. **Select Element**: Choose from validated elements in your dataset
3. **Upload New Files**: Add test files for consistency checking
4. **Run Calibration**: Execute analysis against known good results
5. **Compare Outputs**: Review consistency with previous successful runs
6. **Generate Reports**: View performance metrics and calibration results

## 🛠️ Features Deep Dive

### AI Analysis Methods

#### RAG (Reasoning) Method
- **Use Case**: Complex document analysis requiring context understanding
- **Process**: 
  1. Document chunking with embeddings
  2. Semantic search for relevant content
  3. Context-aware analysis with GPT-4
- **Best For**: Research papers, reports, complex documents

#### Extraction Method
- **Use Case**: Structured data extraction from documents
- **Process**:
  1. GPT-4 generates Python extraction scripts
  2. Iterative script refinement based on results
  3. Autonomous execution with error handling
- **Best For**: Forms, tables, structured documents

### File Management System
- **Supported Formats**: TXT, PDF, DOCX, CSV, PPR-RX, PPR-VX
- **Upload Limits**: 50MB per file (configurable)
- **Storage**: Secure local filesystem with database metadata
- **Security**: File type validation and sanitization
- **API Access**: RESTful endpoints for programmatic access

### Database Schema
```sql
-- Element configurations
dynamic_elements (
    id, name, prompt, ai_model, method, 
    file_type, data_sources, status, created_at, updated_at
)

-- Calibration dataset
dataset_entries (
    id, element_id, element_name, json_config, 
    ai_output, created_at
)

-- File metadata
uploaded_files (
    id, filename, original_filename, file_path, 
    file_size, content_type, element_id, created_at
)
```

## 🧪 Testing Framework

### Playwright E2E Testing
The application includes comprehensive end-to-end testing:

```bash
# Run all tests
npm run test

# Run specific test suites
npm run test:comprehensive  # Full UI workflows
npm run test:api           # Backend API testing
npm run test:errors        # Error handling scenarios
npm run test:basic         # Basic UI interactions

# Run tests with UI
npm run test:ui

# View test reports
npm run test:report
```

### Test Coverage
- **UI Workflows**: Configuration, validation, and calibration flows
- **File Operations**: Upload, download, and deletion
- **API Integration**: All backend endpoints
- **Error Handling**: Network failures, invalid inputs, timeout scenarios
- **Cross-Browser**: Chromium, Firefox, and WebKit compatibility

## 📡 API Documentation

### Core Endpoints

#### Elements API (`/api/v1/elements/`)
```http
GET    /api/v1/elements/           # List all elements
POST   /api/v1/elements/           # Create new element
GET    /api/v1/elements/{id}       # Get element by ID
PUT    /api/v1/elements/{id}       # Update element
DELETE /api/v1/elements/{id}       # Delete element
POST   /api/v1/elements/{id}/validate  # Mark as validated
POST   /api/v1/elements/{id}/analyze   # Run AI analysis
```

#### Dataset API (`/api/v1/dataset/`)
```http
GET    /api/v1/dataset/            # List dataset entries
POST   /api/v1/dataset/            # Create dataset entry
GET    /api/v1/dataset/{id}        # Get dataset entry
DELETE /api/v1/dataset/{id}        # Delete dataset entry
```

#### Files API (`/api/v1/files/`)
```http
POST   /api/v1/files/upload        # Upload files
GET    /api/v1/files/{id}          # Download file
GET    /api/v1/files/              # List files
DELETE /api/v1/files/{id}          # Delete file
```

### Example API Usage

**Create Element:**
```javascript
const element = {
  name: "Invoice Data Extractor",
  prompt: "Extract invoice number, date, amount, and vendor from this invoice",
  aiModel: "gpt-4",
  method: "extraction",
  fileType: "pdf",
  dataSources: ["KPI tables"]
};

const response = await fetch('/api/v1/elements/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(element)
});
```

## 🔧 Development

### Project Structure
```
dynamic-elements-manager/
├── app/                        # Next.js app directory
│   ├── globals.css            # Global styles
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Homepage
├── components/                # React components
│   ├── calibration-modal.tsx  # Testing suite
│   ├── configuration-modal.tsx # Element configuration
│   ├── processing-modal.tsx   # AI processing
│   ├── validation-modal.tsx   # Dashboard and validation
│   └── ui/                    # Reusable UI components
├── contexts/                  # React contexts
│   └── dynamic-elements-context.tsx # Global state management
├── lib/                       # Utilities
│   ├── api.ts                # API client
│   └── types.ts              # TypeScript definitions
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── api/v1/           # API routes
│   │   ├── core/             # Configuration
│   │   ├── crud/             # Database operations
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # AI analysis engines
│   ├── main.py               # FastAPI application
│   ├── run.py                # Development server
│   └── requirements.txt      # Dependencies
├── tests/                     # Playwright tests
└── uploads/                   # File storage (auto-created)
```

### Code Quality & Standards
- **TypeScript**: Strict type checking for frontend
- **Pydantic**: Data validation and serialization for backend
- **SQLAlchemy**: ORM with type hints and relationship management
- **ESLint**: Code linting and formatting
- **Error Handling**: Comprehensive error handling and user feedback

### Development Scripts
```bash
# Frontend development
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linting

# Backend development
cd backend
python run.py        # Start development server
python -m pytest    # Run backend tests (if added)

# Full-stack development
npm run backend      # Start backend from root directory
```

## 🚀 Production Deployment

### Environment Setup
1. **Database**: Migrate from SQLite to PostgreSQL for production
2. **File Storage**: Consider cloud storage (AWS S3, Google Cloud Storage)
3. **API Keys**: Secure OpenAI API key management
4. **CORS**: Configure production frontend URLs
5. **SSL**: Enable HTTPS for production deployment

### Docker Deployment (Optional)
```dockerfile
# Backend Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Considerations
- **Database Connection Pooling**: Configure for high concurrency
- **File Upload Limits**: Adjust based on infrastructure capacity
- **AI API Rate Limits**: Implement retry logic and queue management
- **Caching**: Add Redis for session management and API response caching

## 🔐 Security

### Data Protection
- **File Validation**: Strict file type and size validation
- **SQL Injection**: Protected via SQLAlchemy ORM
- **XSS Protection**: React's built-in XSS protection
- **CORS Configuration**: Restricted to specified origins

### API Security
- **Input Validation**: Pydantic schema validation
- **Error Handling**: Sanitized error messages
- **File Storage**: Secure file path handling
- **Rate Limiting**: Ready for implementation

## 📊 Monitoring & Analytics

### Health Checks
- **Backend Health**: `/health` endpoint for monitoring
- **Database Connectivity**: Automatic database connection testing
- **File System**: Upload directory accessibility verification

### Logging
- **Application Logs**: Structured logging for debugging
- **API Access**: Request/response logging capability
- **Error Tracking**: Comprehensive error logging and tracking

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install dependencies: `npm install && cd backend && pip install -r requirements.txt`
4. Make your changes
5. Run tests: `npm run test`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style
- Follow existing TypeScript and Python conventions
- Add tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📝 Changelog

### Version 1.0.0
- ✅ Initial release with full-stack architecture
- ✅ AI-powered analysis with dual methods (RAG & Extraction)
- ✅ Complete UI workflow (Configuration → Validation → Calibration)
- ✅ File upload and management system
- ✅ Comprehensive E2E testing with Playwright
- ✅ OpenAI GPT-4 integration
- ✅ SQLite database with migration-ready schema

### Upcoming Features
- 🔄 **Multi-AI Provider Support**: Integration with Claude, Gemini, and local models
- 🔄 **Authentication System**: User management and API key handling
- 🔄 **Advanced Analytics**: Performance metrics and usage analytics
- 🔄 **Batch Processing**: Handle multiple files simultaneously
- 🔄 **Cloud Storage**: S3/GCS integration for file storage
- 🔄 **Docker Deployment**: Complete containerization setup

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Backend Connection Failed:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart backend
cd backend && python run.py
```

**Frontend Build Errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**File Upload Issues:**
- Check file size limits (50MB default)
- Verify upload directory permissions
- Ensure supported file types

**AI Analysis Errors:**
- Verify OpenAI API key in backend `.env`
- Check API rate limits
- Review prompt length and complexity

### Getting Help
- **Documentation**: Check the API docs at `/docs`
- **Issues**: Report bugs via GitHub Issues
- **Development**: See contribution guidelines above

---

**Dynamic Elements Manager** - Empowering AI-driven data processing workflows with enterprise-grade reliability and comprehensive testing.