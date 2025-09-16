export interface DynamicElement {
  id: string
  name: string
  prompt: string
  aiModel: string
  method: "reasoning" | "extraction" | "direct"
  fileType: string
  dataSources: string[]
  status: "draft" | "validated"
  createdAt: string
  updatedAt: string
  uploadedFiles?: File[]
  additionalData?: string
}

export interface DynamicElementInput {
  name: string
  prompt: string
  aiModel: string
  method: "reasoning" | "extraction" | "direct"
  fileType: string
  dataSources: string[]
}

export interface DatasetEntry {
  id: string
  elementId: string
  elementName: string
  json2: any // Complete JSON with files and data
  aiOutput: string
  createdAt: string
}
