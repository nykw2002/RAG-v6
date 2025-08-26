"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import type { DynamicElement, DynamicElementInput, DatasetEntry } from "@/lib/types"
import { apiClient, type DynamicElement as APIDynamicElement } from "@/lib/api"

interface DynamicElementsContextType {
  elements: DynamicElement[]
  addElement: (input: DynamicElementInput) => Promise<void>
  updateElement: (id: string, input: Partial<DynamicElementInput>) => Promise<void>
  deleteElement: (id: string) => Promise<void>
  getElementById: (id: string) => DynamicElement | undefined
  validateElement: (id: string) => Promise<void>
  datasetEntries: DatasetEntry[]
  addToDataset: (elementId: string, json2: any, aiOutput: string) => Promise<void>
  deleteDatasetEntry: (id: string) => Promise<void>
  loading: boolean
  error: string | null
}

const DynamicElementsContext = createContext<DynamicElementsContextType | undefined>(undefined)

// Helper function to transform API elements to local format
function transformAPIElement(apiElement: APIDynamicElement): DynamicElement {
  return {
    id: apiElement.id,
    name: apiElement.name,
    prompt: apiElement.prompt,
    aiModel: apiElement.ai_model,
    method: apiElement.method,
    fileType: apiElement.file_type,
    dataSources: apiElement.data_sources,
    status: apiElement.status,
    createdAt: apiElement.created_at,
    updatedAt: apiElement.updated_at,
  }
}

export function DynamicElementsProvider({ children }: { children: ReactNode }) {
  const [elements, setElements] = useState<DynamicElement[]>([])
  const [datasetEntries, setDatasetEntries] = useState<DatasetEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load from API on mount
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        setError(null)
        
        // Load elements from API
        console.log("Loading elements...")
        const apiElements = await apiClient.getElements()
        console.log("API Elements received:", apiElements)
        const transformedElements = apiElements.map(transformAPIElement)
        setElements(transformedElements)
        
        // Load dataset entries from API
        console.log("Loading dataset entries...")
        const apiDataset = await apiClient.getDatasetEntries()
        console.log("API Dataset received:", apiDataset)
        const transformedDataset = apiDataset.map(entry => ({
          id: entry.id,
          elementId: entry.element_id,
          elementName: entry.element_name,
          json2: entry.json_config,
          aiOutput: entry.ai_output,
          createdAt: entry.created_at,
        }))
        setDatasetEntries(transformedDataset)
        console.log("Data loading completed successfully")
      } catch (error) {
        console.error("Error loading data from API:", error)
        setError(error instanceof Error ? error.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
  }, [])

  // API methods

  const addElement = async (input: DynamicElementInput) => {
    try {
      const apiElement = await apiClient.createElement({
        name: input.name,
        prompt: input.prompt,
        ai_model: input.aiModel,
        method: input.method,
        file_type: input.fileType,
        data_sources: input.dataSources,
      })
      const transformedElement = transformAPIElement(apiElement)
      setElements((prev) => [...prev, transformedElement])
    } catch (error) {
      console.error("Error adding element:", error)
      throw error
    }
  }

  const updateElement = async (id: string, input: Partial<DynamicElementInput>) => {
    try {
      const updateData: any = {}
      if (input.name !== undefined) updateData.name = input.name
      if (input.prompt !== undefined) updateData.prompt = input.prompt
      if (input.aiModel !== undefined) updateData.ai_model = input.aiModel
      if (input.method !== undefined) updateData.method = input.method
      if (input.fileType !== undefined) updateData.file_type = input.fileType
      if (input.dataSources !== undefined) updateData.data_sources = input.dataSources
      
      const apiElement = await apiClient.updateElement(id, updateData)
      const transformedElement = transformAPIElement(apiElement)
      setElements((prev) =>
        prev.map((element) =>
          element.id === id ? transformedElement : element,
        ),
      )
    } catch (error) {
      console.error("Error updating element:", error)
      throw error
    }
  }

  const deleteElement = async (id: string) => {
    try {
      await apiClient.deleteElement(id)
      setElements((prev) => prev.filter((element) => element.id !== id))
    } catch (error) {
      console.error("Error deleting element:", error)
      throw error
    }
  }

  const getElementById = (id: string) => {
    return elements.find((element) => element.id === id)
  }

  const validateElement = async (id: string) => {
    try {
      const apiElement = await apiClient.validateElement(id)
      const transformedElement = transformAPIElement(apiElement)
      setElements((prev) =>
        prev.map((element) =>
          element.id === id ? transformedElement : element,
        ),
      )
    } catch (error) {
      console.error("Error validating element:", error)
      throw error
    }
  }

  const addToDataset = async (elementId: string, json2: any, aiOutput: string) => {
    try {
      const element = getElementById(elementId)
      if (!element) throw new Error('Element not found')
      
      const apiEntry = await apiClient.createDatasetEntry({
        element_id: elementId,
        element_name: element.name,
        json_config: json2,
        ai_output: aiOutput,
      })
      
      const transformedEntry = {
        id: apiEntry.id,
        elementId: apiEntry.element_id,
        elementName: apiEntry.element_name,
        json2: apiEntry.json_config,
        aiOutput: apiEntry.ai_output,
        createdAt: apiEntry.created_at,
      }
      setDatasetEntries((prev) => [...prev, transformedEntry])
    } catch (error) {
      console.error("Error adding to dataset:", error)
      throw error
    }
  }

  const deleteDatasetEntry = async (id: string) => {
    try {
      await apiClient.deleteDatasetEntry(id)
      setDatasetEntries((prev) => prev.filter((entry) => entry.id !== id))
    } catch (error) {
      console.error("Error deleting dataset entry:", error)
      throw error
    }
  }

  return (
    <DynamicElementsContext.Provider
      value={{
        elements,
        addElement,
        updateElement,
        deleteElement,
        getElementById,
        validateElement,
        datasetEntries,
        addToDataset,
        deleteDatasetEntry,
        loading,
        error,
      }}
    >
      {children}
    </DynamicElementsContext.Provider>
  )
}

export function useDynamicElements() {
  const context = useContext(DynamicElementsContext)
  if (context === undefined) {
    throw new Error("useDynamicElements must be used within a DynamicElementsProvider")
  }
  return context
}
