"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Settings, CheckCircle, BarChart3 } from "lucide-react"
import { ConfigurationModal } from "@/components/configuration-modal"
import { ValidationModal } from "@/components/validation-modal"
import { CalibrationModal } from "@/components/calibration-modal"
import { useDynamicElements } from "@/contexts/dynamic-elements-context"

export default function HomePage() {
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false)
  const [isValidationModalOpen, setIsValidationModalOpen] = useState(false)
  const [isCalibrationModalOpen, setIsCalibrationModalOpen] = useState(false)
  
  const { loading, error } = useDynamicElements()

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading Dynamic Elements Manager...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-destructive mb-4">Connection Error</h1>
          <p className="text-muted-foreground mb-4">{error}</p>
          <p className="text-sm text-muted-foreground">
            Make sure the backend server is running on{" "}
            <code className="bg-muted px-2 py-1 rounded">http://localhost:8000</code>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto px-2 sm:px-4">
        {/* Header */}
        <div className="text-center mb-8 lg:mb-12">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-4">Dynamic Elements Manager</h1>
          <p className="text-muted-foreground text-sm sm:text-base lg:text-lg">Configure and validate your dynamic elements with ease</p>
        </div>

        {/* Main Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          {/* Configuration Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-4 bg-primary/10 rounded-full w-fit group-hover:bg-primary/20 transition-colors">
                <Settings className="h-8 w-8 text-primary" />
              </div>
              <CardTitle className="text-xl lg:text-2xl font-bold">Configuration</CardTitle>
              <CardDescription className="text-sm lg:text-base">
                Set up your dynamic elements with custom prompts, AI models, and data sources
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button
                onClick={() => setIsConfigModalOpen(true)}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-medium py-2 sm:py-3"
                size="lg"
              >
                Configure Element
              </Button>
            </CardContent>
          </Card>

          {/* Validation Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-4 bg-secondary/10 rounded-full w-fit group-hover:bg-secondary/20 transition-colors">
                <CheckCircle className="h-8 w-8 text-secondary" />
              </div>
              <CardTitle className="text-xl lg:text-2xl font-bold">Validate</CardTitle>
              <CardDescription className="text-sm lg:text-base">
                Review and test your configured dynamic elements in draft mode
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button
                onClick={() => setIsValidationModalOpen(true)}
                variant="outline"
                className="w-full border-secondary text-secondary hover:bg-secondary hover:text-secondary-foreground font-medium py-2 sm:py-3"
                size="lg"
              >
                View Dashboard
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-4 bg-accent/10 rounded-full w-fit group-hover:bg-accent/20 transition-colors">
                <BarChart3 className="h-8 w-8 text-accent-foreground" />
              </div>
              <CardTitle className="text-xl lg:text-2xl font-bold">Calibration & E2E</CardTitle>
              <CardDescription className="text-sm lg:text-base">
                Calibrate models and run end-to-end testing with your dataset
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button
                onClick={() => setIsCalibrationModalOpen(true)}
                variant="outline"
                className="w-full border-accent-foreground text-accent-foreground hover:bg-accent hover:text-accent-foreground font-medium py-2 sm:py-3"
                size="lg"
              >
                Open Testing Suite
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modals */}
      <ConfigurationModal isOpen={isConfigModalOpen} onClose={() => setIsConfigModalOpen(false)} />
      <ValidationModal isOpen={isValidationModalOpen} onClose={() => setIsValidationModalOpen(false)} />
      <CalibrationModal isOpen={isCalibrationModalOpen} onClose={() => setIsCalibrationModalOpen(false)} />
    </div>
  )
}
