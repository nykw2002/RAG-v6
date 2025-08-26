"use client"

import { useEffect, useState } from "react"

export default function TestPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function testAPI() {
      try {
        console.log("Testing API...")
        const response = await fetch("http://localhost:8000/api/v1/elements/")
        const result = await response.json()
        console.log("API Response:", result)
        setData(result)
        setLoading(false)
      } catch (err) {
        console.error("API Error:", err)
        setError(err instanceof Error ? err.message : "API Error")
        setLoading(false)
      }
    }
    testAPI()
  }, [])

  if (loading) {
    return <div className="p-4 sm:p-6 lg:p-8">Loading API test...</div>
  }

  if (error) {
    return <div className="p-4 sm:p-6 lg:p-8 text-red-500">Error: {error}</div>
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-xl sm:text-2xl font-bold mb-4">API Test Page</h1>
      <div className="bg-gray-100 p-3 sm:p-4 rounded">
        <h2 className="font-semibold mb-2 text-sm sm:text-base">API Response ({data?.length} items):</h2>
        <pre className="text-xs sm:text-sm overflow-auto max-h-96">{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  )
}