"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useDynamicElements } from "@/contexts/dynamic-elements-context"
import type { DynamicElement } from "@/lib/types"

interface ConfigurationModalProps {
  isOpen: boolean
  onClose: () => void
  editElement?: DynamicElement | null
}

export function ConfigurationModal({ isOpen, onClose, editElement }: ConfigurationModalProps) {
  const [prompt, setPrompt] = useState("")
  const [aiModel, setAiModel] = useState("")
  const [method, setMethod] = useState<"reasoning" | "extraction" | "">("")
  const [fileType, setFileType] = useState("")
  const [selectedButtons, setSelectedButtons] = useState<string[]>([])
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [elementName, setElementName] = useState("")
  const [saving, setSaving] = useState(false)

  const { addElement, updateElement } = useDynamicElements()

  useEffect(() => {
    if (editElement) {
      setPrompt(editElement.prompt)
      setAiModel(editElement.aiModel)
      setMethod(editElement.method)
      setFileType(editElement.fileType)
      setSelectedButtons(editElement.dataSources)
      setElementName(editElement.name)
    } else {
      setPrompt("")
      setAiModel("")
      setMethod("")
      setFileType("")
      setSelectedButtons([])
      setElementName("")
    }
  }, [editElement, isOpen])

  const buttonOptions = ["KPI tables", "DE", "Other Data"]

  const toggleButton = (button: string) => {
    setSelectedButtons((prev) => (prev.includes(button) ? prev.filter((b) => b !== button) : [...prev, button]))
  }

  const handleSaveClick = () => {
    if (editElement) {
      handleSave()
    } else {
      setShowSaveDialog(true)
    }
  }

  const handleSave = async () => {
    if (!method) return
    if (!editElement && !elementName.trim()) return

    setSaving(true)
    try {
      if (editElement) {
        await updateElement(editElement.id, {
          name: editElement.name,
          prompt,
          aiModel,
          method,
          fileType,
          dataSources: selectedButtons,
        })
        onClose()
      } else {
        await addElement({
          name: elementName,
          prompt,
          aiModel,
          method,
          fileType,
          dataSources: selectedButtons,
        })
        setShowSaveDialog(false)
        setShowPreview(true)
      }
    } catch (error) {
      console.error("Error saving element:", error)
      // TODO: Add proper error handling/toast notification
    } finally {
      setSaving(false)
    }
  }

  const generatePreviewJSON = () => {
    return {
      user_prompt: prompt,
      method: method,
      model: aiModel,
      data_type: selectedButtons.join("/") || "Not specified",
      data: [],
      files: [
        {
          file_name: "",
          file_type: fileType.toUpperCase(),
          file_path: "",
        },
      ],
    }
  }

  const handleClose = () => {
    setShowSaveDialog(false)
    setShowPreview(false)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="configuration-modal">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">
            {showPreview ? "Developer Preview" : editElement ? "Edit Dynamic Element" : "Configure Dynamic Element"}
          </DialogTitle>
        </DialogHeader>

        {showPreview ? (
          <div className="space-y-6 py-4">
            <div className="text-center mb-4">
              <p className="text-sm text-muted-foreground">
                Configuration saved successfully! Here's the generated JSON structure:
              </p>
            </div>

            <div className="bg-muted rounded-lg p-4 max-h-64 overflow-auto">
              <pre className="text-sm font-mono whitespace-pre-wrap break-words">
                {JSON.stringify(generatePreviewJSON(), null, 2)}
              </pre>
            </div>

            <div className="flex justify-center">
              <Button onClick={handleClose} className="bg-primary hover:bg-primary/90 text-primary-foreground px-8">
                Done
              </Button>
            </div>
          </div>
        ) : !showSaveDialog ? (
          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="prompt" className="text-sm font-medium">
                Prompt
              </Label>
              <Textarea
                id="prompt"
                placeholder="Enter your prompt here..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[100px] resize-none"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">AI Model</Label>
              <Select value={aiModel} onValueChange={setAiModel}>
                <SelectTrigger>
                  <SelectValue placeholder="Select AI model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3">Claude 3</SelectItem>
                  <SelectItem value="gemini-pro">Gemini Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Method</Label>
              <Select value={method} onValueChange={(value: "reasoning" | "extraction") => setMethod(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="reasoning">Reasoning</SelectItem>
                  <SelectItem value="extraction">Extraction</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">File Type</Label>
              <Select value={fileType} onValueChange={setFileType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select file type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="txt">TXT</SelectItem>
                  <SelectItem value="ppr-rx">PPR-RX</SelectItem>
                  <SelectItem value="ppr-vx">PPR-VX</SelectItem>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="docx">DOCX</SelectItem>
                  <SelectItem value="csv">CSV</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Data Sources</Label>
              <div className="flex flex-wrap gap-2" data-testid="data-sources">
                {buttonOptions.map((button) => (
                  <Button
                    key={button}
                    variant={selectedButtons.includes(button) ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleButton(button)}
                    data-testid={`data-source-${button.toLowerCase().replace(/\s+/g, '-')}`}
                    className={
                      selectedButtons.includes(button)
                        ? "bg-primary hover:bg-primary/90"
                        : "border-primary text-primary hover:bg-primary hover:text-primary-foreground"
                    }
                  >
                    {button}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <Button onClick={handleSaveClick} disabled={saving} className="bg-primary hover:bg-primary/90 text-primary-foreground px-8">
                {saving ? "Saving..." : editElement ? "Update Configuration" : "Save Configuration"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-6 py-4">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-4">Save Dynamic Element</h3>
              <div className="space-y-2">
                <Label htmlFor="elementName" className="text-sm font-medium">
                  Element Name
                </Label>
                <Input
                  id="elementName"
                  placeholder="Enter element name..."
                  value={elementName}
                  onChange={(e) => setElementName(e.target.value)}
                />
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
                Back
              </Button>
              <Button
                onClick={handleSave}
                disabled={!elementName.trim() || saving}
                className="bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                {saving ? "Saving..." : "Save Element"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
