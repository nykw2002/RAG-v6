const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1'

export interface DynamicElement {
  id: string
  name: string
  prompt: string
  ai_model: string
  method: "reasoning" | "extraction"
  file_type: string
  data_sources: string[]
  status: "draft" | "validated"
  created_at: string
  updated_at: string
}

export interface DynamicElementCreate {
  name: string
  prompt: string
  ai_model: string
  method: "reasoning" | "extraction"
  file_type: string
  data_sources: string[]
}

export interface DatasetEntry {
  id: string
  element_id: string
  element_name: string
  json_config: any
  ai_output: string
  created_at: string
}

export interface DatasetEntryCreate {
  element_id: string
  element_name: string
  json_config: any
  ai_output: string
}

export interface UploadedFile {
  id: string
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  content_type: string
  element_id?: string
  created_at: string
}

class APIClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Dynamic Elements API
  async getElements(): Promise<DynamicElement[]> {
    return this.request<DynamicElement[]>('/elements/')
  }

  async createElement(element: DynamicElementCreate): Promise<DynamicElement> {
    return this.request<DynamicElement>('/elements/', {
      method: 'POST',
      body: JSON.stringify(element),
    })
  }

  async getElement(id: string): Promise<DynamicElement> {
    return this.request<DynamicElement>(`/elements/${id}`)
  }

  async updateElement(id: string, element: Partial<DynamicElementCreate>): Promise<DynamicElement> {
    return this.request<DynamicElement>(`/elements/${id}`, {
      method: 'PUT',
      body: JSON.stringify(element),
    })
  }

  async deleteElement(id: string): Promise<void> {
    await this.request(`/elements/${id}`, {
      method: 'DELETE',
    })
  }

  async validateElement(id: string): Promise<DynamicElement> {
    return this.request<DynamicElement>(`/elements/${id}/validate`, {
      method: 'POST',
    })
  }

  // Dataset API
  async getDatasetEntries(): Promise<DatasetEntry[]> {
    return this.request<DatasetEntry[]>('/dataset/')
  }

  async createDatasetEntry(entry: DatasetEntryCreate): Promise<DatasetEntry> {
    return this.request<DatasetEntry>('/dataset/', {
      method: 'POST',
      body: JSON.stringify(entry),
    })
  }

  async deleteDatasetEntry(id: string): Promise<void> {
    await this.request(`/dataset/${id}`, {
      method: 'DELETE',
    })
  }

  // Files API
  async uploadFiles(files: File[], elementId?: string): Promise<UploadedFile[]> {
    const formData = new FormData()
    
    files.forEach(file => {
      formData.append('files', file)
    })
    
    if (elementId) {
      formData.append('element_id', elementId)
    }

    return this.request<UploadedFile[]>('/files/upload', {
      method: 'POST',
      headers: {}, // Remove Content-Type header to let browser set it for FormData
      body: formData,
    })
  }

  async getFiles(elementId?: string): Promise<UploadedFile[]> {
    const params = elementId ? `?element_id=${elementId}` : ''
    return this.request<UploadedFile[]>(`/files/${params}`)
  }

  async deleteFile(id: string): Promise<void> {
    await this.request(`/files/${id}`, {
      method: 'DELETE',
    })
  }

  getFileUrl(id: string): string {
    return `${this.baseURL}/files/${id}`
  }

  // AI Analysis API
  async analyzeElement(elementId: string, files: File[], additionalData?: string): Promise<{
    success: boolean
    analysis_result: string
    element_id: string
    files_processed: number
    method_used: string
  }> {
    const formData = new FormData()
    
    files.forEach(file => {
      formData.append('files', file)
    })
    
    if (additionalData) {
      formData.append('additional_data', additionalData)
    }

    return this.request(`/elements/${elementId}/analyze`, {
      method: 'POST',
      headers: {}, // Remove Content-Type header to let browser set it for FormData
      body: formData,
    })
  }
}

export const apiClient = new APIClient()
export default apiClient