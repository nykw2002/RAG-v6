"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Upload, FileText, Play, Check, X } from "lucide-react"
import type { DynamicElement } from "@/lib/types"
import { apiClient } from "@/lib/api"

interface ProcessingModalProps {
  isOpen: boolean
  onClose: () => void
  element: DynamicElement | null
  onValidate: (elementId: string) => void
  onAddToDataset?: (elementId: string, json: any, aiOutput: string) => void
  skipToResults?: boolean
}

export function ProcessingModal({
  isOpen,
  onClose,
  element,
  onValidate,
  onAddToDataset,
  skipToResults = false,
}: ProcessingModalProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [additionalData, setAdditionalData] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [aiOutput, setAiOutput] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  useEffect(() => {
    if (skipToResults && element?.status === "validated") {
      // For validated elements, we'll show a message indicating they need to be run again for new analysis
      setAiOutput(`This element has been validated previously.

To perform a new analysis:
1. Upload your files
2. Click "Run Analysis" to get fresh AI insights

The previous validation status will be maintained, but you can generate new analysis results based on your current files and data.`)
    }
  }, [skipToResults, element])

  if (!element) return null

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    setUploadedFiles((prev) => [...prev, ...files])
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      setUploadedFiles((prev) => [...prev, ...files])
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleRun = async () => {
    if (!element || uploadedFiles.length === 0) {
      return
    }

    setIsProcessing(true)

    try {
      // Call the real AI analysis API
      const result = await apiClient.analyzeElement(
        element.id,
        uploadedFiles,
        additionalData
      )

      if (result.success) {
        setAiOutput(result.analysis_result)
      } else {
        setAiOutput("Analysis failed. Please try again.")
      }
    } catch (error) {
      console.error("Analysis error:", error)
      setAiOutput("Error during analysis. Please check your files and try again.")
    } finally {
      setIsProcessing(false)
    }
  }

  const handleKeepDraft = () => {
    setUploadedFiles([])
    setAdditionalData("")
    setAiOutput(null)
    onClose()
  }

  const handleValidate = () => {
    onValidate(element.id)
    setUploadedFiles([])
    setAdditionalData("")
    setAiOutput(null)
    onClose()
  }

  const generateCompleteJSON = () => {
    return {
      user_prompt: element.prompt,
      method: element.method,
      model: element.aiModel,
      data_type: element.dataSources.join(", "),
      data: additionalData ? [additionalData] : [],
      files: uploadedFiles.map((file) => ({
        file_name: file.name,
        file_type: element.fileType.toUpperCase(),
        file_path: `uploads/${file.name}`,
      })),
    }
  }

  const handleAddToDataset = () => {
    if (onAddToDataset && aiOutput) {
      const completeJSON = generateCompleteJSON()
      onAddToDataset(element.id, completeJSON, aiOutput)
      setUploadedFiles([])
      setAdditionalData("")
      setAiOutput(null)
      onClose()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="w-[80vw] h-[80vh] max-w-none max-h-none overflow-y-auto"
        data-testid="processing-modal"
        style={{ width: "80vw", height: "80vh" }}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Play className="h-5 w-5 text-orange-500" />
            Process: {element.name}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {!aiOutput && !skipToResults ? (
            <>
              {/* File Upload Section */}
              <div className="space-y-4">
                <Label className="text-sm font-medium">Upload {element.fileType.toUpperCase()} Files</Label>
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive ? "border-orange-500 bg-orange-50" : "border-gray-300 hover:border-orange-400"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-sm text-gray-600 mb-2">
                    Drag and drop your {element.fileType.toUpperCase()} files here, or
                  </p>
                  <Button variant="outline" size="sm" asChild>
                    <label className="cursor-pointer">
                      Browse Files
                      <input
                        type="file"
                        multiple
                        accept={`.${element.fileType.toLowerCase()}`}
                        onChange={handleFileInput}
                        className="hidden"
                      />
                    </label>
                  </Button>
                </div>

                {/* Uploaded Files List */}
                {uploadedFiles.length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Uploaded Files:</Label>
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{file.name}</span>
                          <Badge variant="secondary" className="text-xs">
                            {(file.size / 1024).toFixed(1)} KB
                          </Badge>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => removeFile(index)}>
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Additional Data Section */}
              <div className="space-y-4">
                <Label className="text-sm font-medium">Additional Data Source ({element.dataSources.join(", ")})</Label>
                <Input
                  placeholder="Enter data source path or connection string..."
                  value={additionalData}
                  onChange={(e) => setAdditionalData(e.target.value)}
                />
              </div>

              {/* Configuration Preview */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Configuration Preview:</Label>
                <div className="bg-gray-50 p-4 rounded max-h-32 overflow-auto">
                  <pre className="text-xs break-words whitespace-pre-wrap">
                    {JSON.stringify(generateCompleteJSON(), null, 2)}
                  </pre>
                </div>
              </div>

              {/* Run Button */}
              <Button onClick={handleRun} disabled={uploadedFiles.length === 0 || isProcessing} className="w-full">
                {isProcessing ? "Processing..." : "Run Analysis"}
              </Button>
            </>
          ) : (
            <>
              {/* AI Output Section */}
              <div className="space-y-4">
                <Label className="text-sm font-medium flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  AI Analysis Results
                </Label>
                <div className="bg-gray-50 p-6 rounded-lg max-h-64 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm break-words">{aiOutput}</pre>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-3 gap-4">
                <Button variant="outline" onClick={handleKeepDraft} className="bg-transparent">
                  Keep in Draft
                </Button>
                <Button onClick={handleValidate} className="bg-green-600 hover:bg-green-700">
                  Validate
                </Button>
                <Button onClick={handleAddToDataset} className="bg-blue-600 hover:bg-blue-700" disabled={!aiOutput}>
                  Add to Dataset
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
