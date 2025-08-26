"use client"

import type React from "react"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Trash2, Calendar, Upload } from "lucide-react"
import { useDynamicElements } from "@/contexts/dynamic-elements-context"
import { useState, useCallback } from "react"

interface CalibrationModalProps {
  isOpen: boolean
  onClose: () => void
}

export function CalibrationModal({ isOpen, onClose }: CalibrationModalProps) {
  const { datasetEntries, deleteDatasetEntry } = useDynamicElements()
  const [selectedElementId, setSelectedElementId] = useState<string>("")
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [calibrationOutput, setCalibrationOutput] = useState<string>("")
  const [isCalibrating, setIsCalibrating] = useState(false)

  const selectedElement = datasetEntries.find((entry) => entry.id === selectedElementId)

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setUploadedFiles(files)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const files = Array.from(e.dataTransfer.files)
    setUploadedFiles(files)
  }, [])

  const handleCalibrate = async () => {
    if (!selectedElement || uploadedFiles.length === 0) return

    setIsCalibrating(true)

    setTimeout(() => {
      const mockOutput = `Calibration Results for "${selectedElement.elementName}":

Configuration Used:
- Model: ${selectedElement.json2.model}
- Method: ${selectedElement.json2.method}
- Data Type: ${selectedElement.json2.data_type}
- Files Processed: ${uploadedFiles.map((f) => f.name).join(", ")}

AI Analysis Output:
This is a simulated calibration result. The system processed ${uploadedFiles.length} file(s) using the ${selectedElement.json2.model} model with ${selectedElement.json2.method} method.

Performance Metrics:
- Processing Time: 2.3s
- Confidence Score: 87%
- Data Quality: Good

You can now compare this output with the saved dataset entry to validate consistency.`

      setCalibrationOutput(mockOutput)
      setIsCalibrating(false)
    }, 2000)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="overflow-hidden flex flex-col"
        data-testid="calibration-modal"
        style={{
          width: "90vw",
          maxWidth: "90vw",
          height: "80vh",
          maxHeight: "80vh",
        }}
      >
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Calibration & E2E Testing</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-6 flex-1 min-h-0">
          <div className="flex flex-col border-r pr-6 h-full">
            {/* Top left section - Testing controls */}
            <div className="flex-1 flex flex-col border border-gray-300 rounded-lg p-4 mb-4">
              <h3 className="text-lg font-semibold mb-4">Element Testing</h3>

              {/* Choose element dropdown */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Choose an element for testing</label>
                <Select value={selectedElementId} onValueChange={setSelectedElementId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a dataset element..." />
                  </SelectTrigger>
                  <SelectContent>
                    {datasetEntries.map((entry) => (
                      <SelectItem key={entry.id} value={entry.id}>
                        {entry.elementName} - {entry.json2.method} ({entry.json2.model})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* File upload area */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add needed files
                  {selectedElement && (
                    <span className="text-xs text-gray-500 ml-2">
                      (Required: {selectedElement.json2.files[0]?.file_type || "Any"} files)
                    </span>
                  )}
                </label>
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors cursor-pointer"
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById("file-upload")?.click()}
                >
                  <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">
                    {uploadedFiles.length > 0
                      ? `${uploadedFiles.length} file(s) selected: ${uploadedFiles.map((f) => f.name).join(", ")}`
                      : "Drag and drop files here, or click to select"}
                  </p>
                  <input id="file-upload" type="file" multiple className="hidden" onChange={handleFileUpload} />
                </div>
              </div>

              {/* Calibrate button */}
              <Button
                onClick={handleCalibrate}
                disabled={!selectedElement || uploadedFiles.length === 0 || isCalibrating}
                className="w-full bg-orange-500 hover:bg-orange-600"
              >
                {isCalibrating ? "Calibrating..." : "Calibrate"}
              </Button>
            </div>

            {/* Bottom left section - AI output */}
            <div className="flex-1 flex flex-col border border-gray-300 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Calibration Output</h3>
              <div className="flex-1 bg-gray-50 rounded p-3 overflow-auto">
                {calibrationOutput ? (
                  <pre className="text-sm whitespace-pre-wrap text-gray-800">{calibrationOutput}</pre>
                ) : (
                  <p className="text-gray-500 text-sm">
                    Select an element, upload files, and click "Calibrate" to see the AI output here.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Right side - Dataset entries table */}
          <div className="flex flex-col h-full pl-6 min-h-0">
            <div className="mb-4 flex-shrink-0">
              <h3 className="text-lg font-semibold mb-2">Dataset Entries</h3>
              <Badge variant="secondary" className="text-xs">
                {datasetEntries.length} entries
              </Badge>
            </div>

            <div className="flex-1 overflow-y-auto border border-gray-300 rounded-lg min-h-0">
              {datasetEntries.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No dataset entries yet.</p>
                  <p className="text-sm">Add entries from the validation workflow.</p>
                </div>
              ) : (
                <div className="overflow-hidden">
                  <table className="w-full border-collapse">
                    <thead className="bg-gray-100 sticky top-0 z-10">
                      <tr>
                        <th className="border border-gray-300 px-2 py-2 text-left text-xs font-semibold text-gray-700" style={{width: "45%"}}>
                          JSON Configuration
                        </th>
                        <th className="border border-gray-300 px-2 py-2 text-left text-xs font-semibold text-gray-700" style={{width: "45%"}}>
                          AI Analysis Results
                        </th>
                        <th className="border border-gray-300 px-2 py-2 text-center text-xs font-semibold text-gray-700" style={{width: "10%"}}>
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {datasetEntries.map((entry, index) => (
                        <tr key={entry.id} className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                          <td className="border border-gray-300 px-2 py-2 align-top" style={{width: "45%"}}>
                            <div className="mb-2">
                              <div className="text-xs font-medium text-gray-600 mb-1 flex items-center gap-2 flex-wrap">
                                <span className="break-words">{entry.elementName}</span>
                                <div className="flex items-center gap-1 text-gray-400 flex-shrink-0">
                                  <Calendar className="h-3 w-3" />
                                  <span>{new Date(entry.createdAt).toLocaleDateString()}</span>
                                </div>
                              </div>
                            </div>
                            <div className="bg-gray-100 p-2 rounded max-h-32 overflow-auto">
                              <pre className="text-xs font-mono whitespace-pre-wrap break-all">
                                {JSON.stringify(entry.json2, null, 2)}
                              </pre>
                            </div>
                          </td>
                          <td className="border border-gray-300 px-2 py-2 align-top" style={{width: "45%"}}>
                            <div className="bg-gray-100 p-2 rounded max-h-32 overflow-auto">
                              <p className="text-xs whitespace-pre-wrap break-all leading-tight">
                                {entry.aiOutput}
                              </p>
                            </div>
                          </td>
                          <td className="border border-gray-300 px-2 py-2 text-center align-top" style={{width: "10%"}}>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteDatasetEntry(entry.id)}
                              className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
