import * as React from "react"

interface SelectProps {
  value?: string
  onValueChange?: (value: string) => void
  children: React.ReactNode
}

const Select = ({ value, onValueChange, children }: SelectProps) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const [selectedValue, setSelectedValue] = React.useState(value || "")

  React.useEffect(() => {
    setSelectedValue(value || "")
  }, [value])

  const handleValueChange = (newValue: string) => {
    setSelectedValue(newValue)
    onValueChange?.(newValue)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            isOpen,
            setIsOpen,
            selectedValue,
            onValueChange: handleValueChange,
          })
        }
        return child
      })}
    </div>
  )
}

interface SelectTriggerProps {
  children: React.ReactNode
  isOpen?: boolean
  setIsOpen?: (open: boolean) => void
  selectedValue?: string
}

const SelectTrigger = ({ children, isOpen, setIsOpen, selectedValue }: SelectTriggerProps) => (
  <button
    type="button"
    className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    onClick={() => setIsOpen?.(!isOpen)}
  >
    {React.Children.map(children, (child) => {
      if (React.isValidElement(child)) {
        return React.cloneElement(child as React.ReactElement<any>, {
          selectedValue,
        })
      }
      return child
    })}
    <span className="ml-2">▼</span>
  </button>
)

interface SelectValueProps {
  placeholder?: string
  selectedValue?: string
}

const SelectValue = ({ placeholder, selectedValue }: SelectValueProps) => {
  return (
    <span className="text-left">
      {selectedValue || placeholder}
    </span>
  )
}

interface SelectContentProps {
  children: React.ReactNode
  isOpen?: boolean
  onValueChange?: (value: string) => void
}

const SelectContent = ({ children, isOpen, onValueChange }: SelectContentProps) => {
  if (!isOpen) return null

  return (
    <div className="absolute top-full left-0 z-50 w-full mt-1 bg-background border border-input rounded-md shadow-lg max-h-60 overflow-auto">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            onValueChange,
          })
        }
        return child
      })}
    </div>
  )
}

interface SelectItemProps {
  value: string
  children: React.ReactNode
  onValueChange?: (value: string) => void
}

const SelectItem = ({ value, children, onValueChange }: SelectItemProps) => (
  <div
    className="px-3 py-2 text-sm hover:bg-accent hover:text-accent-foreground cursor-pointer"
    onClick={() => onValueChange?.(value)}
  >
    {children}
  </div>
)

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }