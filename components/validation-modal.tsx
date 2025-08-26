"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Settings, FileText, Brain, Database, Trash2 } from "lucide-react"
import { useDynamicElements } from "@/contexts/dynamic-elements-context"
import { ProcessingModal } from "./processing-modal"
import { ConfigurationModal } from "./configuration-modal"
import type { DynamicElement } from "@/lib/types"

interface ValidationModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ValidationModal({ isOpen, onClose }: ValidationModalProps) {
  const { elements, deleteElement, validateElement, addToDataset } = useDynamicElements()
  const [processingModalOpen, setProcessingModalOpen] = useState(false)
  const [configModalOpen, setConfigModalOpen] = useState(false)
  const [selectedElement, setSelectedElement] = useState<DynamicElement | null>(null)
  const [skipToResults, setSkipToResults] = useState(false)

  const getMethodIcon = (method: string) => {
    return method === "reasoning" ? <Brain className="h-4 w-4" /> : <Database className="h-4 w-4" />
  }

  const getFileTypeIcon = () => <FileText className="h-4 w-4" />

  const handleCardClick = (element: DynamicElement) => {
    setSelectedElement(element)
    if (element.status === "validated") {
      // Skip to AI results for validated elements
      setSkipToResults(true)
      setProcessingModalOpen(true)
    } else {
      // Normal flow for draft elements
      setSkipToResults(false)
      setProcessingModalOpen(true)
    }
  }

  const handleTest = (element: DynamicElement) => {
    setSelectedElement(element)
    setSkipToResults(false)
    setProcessingModalOpen(true)
  }

  const handleValidate = (elementId: string) => {
    validateElement(elementId)
    setProcessingModalOpen(false)
    setSelectedElement(null)
  }

  const handleAddToDataset = (elementId: string, json: any, aiOutput: string) => {
    addToDataset(elementId, json, aiOutput)
    setProcessingModalOpen(false)
    setSelectedElement(null)
  }

  const handleEditConfig = (element: DynamicElement) => {
    setSelectedElement(element)
    setProcessingModalOpen(false)
    setConfigModalOpen(true)
  }

  const handleCloseProcessing = () => {
    setProcessingModalOpen(false)
    setSelectedElement(null)
    setSkipToResults(false)
  }

  const handleConfigSaved = () => {
    setConfigModalOpen(false)
    // Return to processing modal (file upload step) after config edit
    if (selectedElement) {
      setSkipToResults(false)
      setProcessingModalOpen(true)
    }
  }

  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent
          className="overflow-y-auto"
          data-testid="validation-modal"
          style={{
            width: "90vw",
            maxWidth: "90vw",
            height: "90vh",
            maxHeight: "90vh",
          }}
        >
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">Dynamic Elements Dashboard</DialogTitle>
          </DialogHeader>

          <div className="py-4">
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Dynamic Elements</h3>
              <p className="text-muted-foreground text-sm">Review and test your configured dynamic elements</p>
            </div>

            {elements.length === 0 ? (
              <div className="text-center py-12">
                <Settings className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Elements Configured</h3>
                <p className="text-muted-foreground">Create your first dynamic element using the Configuration card</p>
              </div>
            ) : (
              <div className="grid grid-cols-6 gap-3">
                {elements.map((element) => (
                  <Card
                    key={element.id}
                    className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => handleCardClick(element)}
                  >
                    <CardHeader className="pb-2 px-3 pt-3">
                      <div className="flex items-start justify-between">
                        <div className="min-w-0 flex-1">
                          <CardTitle className="text-sm font-semibold truncate">{element.name}</CardTitle>
                          <CardDescription className="text-xs mt-1">
                            {new Date(element.createdAt).toLocaleDateString()}
                          </CardDescription>
                        </div>
                        <Badge
                          variant={element.status === "validated" ? "default" : "secondary"}
                          className={`text-xs ml-2 flex-shrink-0 ${
                            element.status === "validated"
                              ? "bg-green-500 text-white hover:bg-green-600 border-green-500"
                              : "bg-orange-100 text-orange-800 hover:bg-orange-100"
                          }`}
                        >
                          {element.status === "validated" ? "Validated" : "Draft"}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3 px-3 pb-3">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Prompt:</p>
                        <div className="text-xs bg-muted p-2 rounded text-foreground max-h-16 overflow-y-auto">
                          <p className="break-words whitespace-pre-wrap leading-tight">
                            {element.prompt.length > 100 
                              ? `${element.prompt.substring(0, 100)}...` 
                              : element.prompt
                            }
                          </p>
                        </div>
                      </div>

                      <div className="space-y-2 text-xs">
                        <div>
                          <p className="text-muted-foreground mb-1">Model:</p>
                          <div className="flex items-center gap-1">
                            <Brain className="h-3 w-3 text-primary flex-shrink-0" />
                            <span className="font-medium truncate">{element.aiModel}</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-muted-foreground mb-1">Method:</p>
                          <div className="flex items-center gap-1">
                            {getMethodIcon(element.method)}
                            <span className="font-medium capitalize">{element.method}</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-muted-foreground mb-1">File:</p>
                          <div className="flex items-center gap-1">
                            {getFileTypeIcon()}
                            <span className="font-medium uppercase">{element.fileType}</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-muted-foreground mb-1">Sources:</p>
                          <div className="flex flex-wrap gap-1">
                            {element.dataSources.map((source) => (
                              <Badge key={source} variant="outline" className="text-xs px-1 py-0">
                                {source}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="flex justify-between gap-1 pt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          data-testid={`delete-element-${element.id}`}
                          onClick={async (e) => {
                            e.stopPropagation()
                            try {
                              await deleteElement(element.id)
                            } catch (error) {
                              console.error("Error deleting element:", error)
                            }
                          }}
                          className="text-destructive hover:text-destructive-foreground hover:bg-destructive h-7 w-7 p-0"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          data-testid={`edit-element-${element.id}`}
                          className="text-xs px-2 h-7 bg-transparent"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleEditConfig(element)
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          data-testid={`test-element-${element.id}`}
                          className="bg-primary hover:bg-primary/90 text-xs px-2 h-7"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleTest(element)
                          }}
                        >
                          Test
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <ProcessingModal
        isOpen={processingModalOpen}
        onClose={handleCloseProcessing}
        element={selectedElement}
        onValidate={handleValidate}
        onAddToDataset={handleAddToDataset}
        skipToResults={skipToResults}
      />

      <ConfigurationModal isOpen={configModalOpen} onClose={handleConfigSaved} editElement={selectedElement} />
    </>
  )
}
