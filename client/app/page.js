"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Upload,
  Search,
  FileText,
  Clock,
  Settings,
  CheckCircle,
  Loader2,
  Copy,
  Trash2,
  Brain,
  ChevronDown,
  Database,
  Cpu,
  ArrowRight,
  X,
  BarChart3,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Textarea } from "@/components/ui/textarea"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const architectures = [
  {
    id: "simple",
    name: "Simple RAG",
    description: "Fast semantic search with vector embeddings",
    icon: <Search className="w-5 h-5" />,
    complexity: "Basic",
    useCase: "Quick answers from documents",
  },
  {
    id: "reranking",
    name: "Reranker RAG",
    description: "Enhanced precision with cross-encoder reranking",
    icon: <Brain className="w-5 h-5" />,
    complexity: "Advanced",
    useCase: "Complex queries requiring high accuracy",
  },
  {
    id: "hyde",
    name: "HyDE RAG",
    description: "Hypothetical document embeddings for better understanding",
    icon: <BarChart3 className="w-5 h-5" />,
    complexity: "Expert",
    useCase: "Abstract concepts and complex reasoning",
  },
]

export default function RAGPlayground() {
  const [availableArchitectures, setAvailableArchitectures] = useState([])
  const [selectedArchitectures, setSelectedArchitectures] = useState(["simple"])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [documentStatus, setDocumentStatus] = useState(null)
  const [query, setQuery] = useState("")
  const [results, setResults] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState("upload")
  const [showAllFiles, setShowAllFiles] = useState(false)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    fetchHealthStatus()
    fetchDocumentStatus()
  }, [])

  const fetchHealthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`)
      const data = await response.json()
      setAvailableArchitectures(data.available_architectures)
      setIsConnected(true)
    } catch (err) {
      setError("Failed to connect to the server")
      setIsConnected(false)
    }
  }

  const fetchDocumentStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/status`)
      const data = await response.json()
      setDocumentStatus(data)
    } catch (err) {
      console.error("Failed to fetch document status")
    }
  }

  const handleFileUpload = async (files) => {
    if (!files.length) return

    setIsUploading(true)
    setUploadProgress(0)
    setError(null)

    const formData = new FormData()
    const newFiles = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      status: "uploading",
      progress: 0,
    }))

    setUploadedFiles((prev) => [...prev, ...newFiles])

    Array.from(files).forEach((file) => {
      formData.append("files", file)
    })

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch(`${API_BASE_URL}/api/v1/upload-documents`, {
        method: "POST",
        body: formData,
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      const data = await response.json()
      setDocumentStatus(data)

      setUploadedFiles((prev) =>
        prev.map((file) =>
          newFiles.some((nf) => nf.id === file.id) ? { ...file, status: "completed", progress: 100 } : file,
        ),
      )

      setTimeout(() => {
        setUploadProgress(0)
        setIsUploading(false)
      }, 1000)
    } catch (err) {
      setError("Failed to upload documents")
      setIsUploading(false)
      setUploadProgress(0)
      setUploadedFiles((prev) =>
        prev.map((file) => (newFiles.some((nf) => nf.id === file.id) ? { ...file, status: "failed" } : file)),
      )
    }
  }

  const handleQuery = async () => {
    if (!query.trim() || selectedArchitectures.length === 0) return

    setIsQuerying(true)
    setActiveTab("results")
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query.trim(),
          architectures: selectedArchitectures,
          k: 5,
          show_context: true,
        }),
      })

      if (!response.ok) {
        throw new Error("Query failed")
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError("Failed to process query")
    } finally {
      setIsQuerying(false)
    }
  }

  const clearDocuments = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/v1/documents`, {
        method: "DELETE",
      })
      setDocumentStatus(null)
      setUploadedFiles([])
      setResults(null)
    } catch (err) {
      setError("Failed to clear documents")
    }
  }

  const removeFile = (fileId) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId))
  }

  const handleArchitectureToggle = (archId) => {
    setSelectedArchitectures((prev) => (prev.includes(archId) ? prev.filter((id) => id !== archId) : [...prev, archId]))
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  const filesToDisplay = showAllFiles ? uploadedFiles : uploadedFiles.slice(0, 3)
  const hasMoreFiles = uploadedFiles.length > 3

  const resultEntries = results
    ? Object.entries(
      results.results.reduce(
        (acc, result) => {
          acc[result.architecture] = result
          return acc
        },
      ),
    )
    : []

  const tabs = [
    { id: "upload", label: "Upload", icon: Upload },
    { id: "configure", label: "Configure", icon: Settings },
    { id: "query", label: "Query", icon: Search },
    { id: "results", label: "Results", icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50"
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">RAG Playground</h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm text-gray-600 hidden sm:inline">
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
              <Badge variant="outline" className="hidden sm:inline-flex">
                {uploadedFiles.filter((f) => f.status === "completed").length} docs
              </Badge>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 bg-white sticky top-16 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`relative flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${activeTab === id
                    ? "border-gray-900 text-gray-900"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Error Alert */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-4"
          >
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {/* Upload Tab */}
          {activeTab === "upload" && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">Upload Documents</h2>
                <p className="text-gray-600">Upload PDF documents to create your knowledge base</p>
              </div>

              {/* Upload Area */}
              <Card className="border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors">
                <div className="p-8 text-center">
                  <input
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Upload PDF Files</h3>
                    <p className="text-gray-600 mb-4">Drag and drop files here, or click to browse</p>
                  </label>
                </div>
              </Card>

              {/* Upload Progress */}
              <AnimatePresence>
                {isUploading && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <Card className="p-4">
                      <div className="flex items-center space-x-3 mb-3">
                        <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                        <span className="font-medium text-gray-900">Processing Documents...</span>
                      </div>
                      <Progress value={uploadProgress} className="w-full" />
                      <p className="text-sm text-gray-600 mt-2">{uploadProgress}% complete</p>
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Uploaded Files */}
              <AnimatePresence>
                {uploadedFiles.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <Card>
                      <div className="p-4 border-b border-gray-200">
                        <div className="flex items-center justify-between">
                          <h3 className="font-medium text-gray-900">Uploaded Documents</h3>
                          <Badge variant="outline" className="text-green-600 border-green-200">
                            {uploadedFiles.filter((f) => f.status === "completed").length} Ready
                          </Badge>
                        </div>
                      </div>
                      <div className="divide-y divide-gray-200">
                        {filesToDisplay.map((file, index) => (
                          <motion.div
                            key={file.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="p-4 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                                  <FileText className="w-5 h-5 text-red-600" />
                                </div>
                                <div>
                                  <div className="font-medium text-gray-900">{file.name}</div>
                                  <div className="text-sm text-gray-500">{formatFileSize(file.size)}</div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <div className="flex items-center space-x-2">
                                  {file.status === "uploading" && (
                                    <div className="flex items-center space-x-2 text-blue-600">
                                      <Loader2 className="w-4 h-4 animate-spin" />
                                      <span className="text-sm">Uploading...</span>
                                    </div>
                                  )}
                                  {file.status === "processing" && (
                                    <div className="flex items-center space-x-2 text-orange-600">
                                      <Loader2 className="w-4 h-4 animate-spin" />
                                      <span className="text-sm">Processing...</span>
                                    </div>
                                  )}
                                  {file.status === "completed" && (
                                    <div className="flex items-center space-x-2 text-green-600">
                                      <CheckCircle className="w-4 h-4" />
                                      <span className="text-sm">Ready</span>
                                    </div>
                                  )}
                                  {file.status === "failed" && (
                                    <div className="flex items-center space-x-2 text-red-600">
                                      <X className="w-4 h-4" />
                                      <span className="text-sm">Failed</span>
                                    </div>
                                  )}
                                </div>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => removeFile(file.id)}
                                  className="text-gray-400 hover:text-red-600"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                      {hasMoreFiles && (
                        <div className="p-4 border-t border-gray-200 text-center">
                          <Button
                            variant="ghost"
                            onClick={() => setShowAllFiles(!showAllFiles)}
                            className="text-gray-600 hover:text-gray-900"
                          >
                            {showAllFiles ? "Show Less" : `Show ${uploadedFiles.length - 3} More Files`}
                            <ChevronDown
                              className={`w-4 h-4 ml-2 transition-transform ${showAllFiles ? "rotate-180" : ""}`}
                            />
                          </Button>
                        </div>
                      )}
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>

            </motion.div>
          )}

          {/* Configure Tab */}
          {activeTab === "configure" && (
            <motion.div
              key="configure"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">Configure RAG Architectures</h2>
                <p className="text-gray-600">Select the RAG architectures you want to compare</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {architectures.map((arch, index) => (
                  <motion.div
                    key={arch.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="cursor-pointer"
                    onClick={() => handleArchitectureToggle(arch.id)}
                  >
                    <Card
                      className={`transition-all duration-200 hover:shadow-md ${selectedArchitectures.includes(arch.id)
                          ? "border-gray-900 bg-gray-50"
                          : "border-gray-200 hover:border-gray-300"
                        }`}
                    >
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                              {arch.icon}
                            </div>
                            <div>
                              <h3 className="font-medium text-gray-900">{arch.name}</h3>
                              <Badge variant="outline" className="text-xs mt-1">
                                {arch.complexity}
                              </Badge>
                            </div>
                          </div>
                          <AnimatePresence>
                            {selectedArchitectures.includes(arch.id) && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                exit={{ scale: 0 }}
                                transition={{ type: "spring", stiffness: 300 }}
                              >
                                <CheckCircle className="w-5 h-5 text-gray-900" />
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>

                        <p className="text-gray-600 text-sm mb-4">{arch.description}</p>

                        <div className="pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-500 mb-1">Best for:</p>
                          <p className="text-sm text-gray-700">{arch.useCase}</p>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>

              {/* Selection Summary */}
              <AnimatePresence>
                {selectedArchitectures.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <Card className="border-blue-200 bg-blue-50">
                      <div className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-blue-900">
                              {selectedArchitectures.length} Architecture{selectedArchitectures.length > 1 ? "s" : ""}{" "}
                              Selected
                            </h3>
                            <p className="text-sm text-blue-700">Ready for comparison testing</p>
                          </div>
                          <Button
                            onClick={() => setActiveTab("query")}
                            className="bg-gray-900 hover:bg-gray-800 text-white"
                          >
                            Continue
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* Query Tab */}
          {activeTab === "query" && (
            <motion.div
              key="query"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">Query Your Documents</h2>
                <p className="text-gray-600">Ask questions and compare responses across different RAG architectures</p>
              </div>

              {/* Query Input */}
              <Card>
                <div className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">Your Question</label>
                    <Textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="What would you like to know about your documents?"
                      className="w-full h-32 resize-none"
                    />
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Database className="w-4 h-4" />
                        <span>{uploadedFiles.filter((f) => f.status === "completed").length} documents</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Cpu className="w-4 h-4" />
                        <span>{selectedArchitectures.length} architectures</span>
                      </div>
                    </div>
                    <Button
                      onClick={handleQuery}
                      disabled={!query.trim() || selectedArchitectures.length === 0 || !documentStatus || isQuerying}
                      className="bg-gray-900 hover:bg-gray-800 text-white"
                    >
                      {isQuerying ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Search className="w-4 h-4 mr-2" />
                          Compare Results
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Selected Architectures */}
              <AnimatePresence>
                {selectedArchitectures.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <Card>
                      <div className="p-4">
                        <h3 className="font-medium text-gray-900 mb-3">Selected Architectures</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                          {selectedArchitectures.map((archId) => {
                            const arch = architectures.find((a) => a.id === archId)
                            if (!arch) return null
                            return (
                              <div
                                key={archId}
                                className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
                              >
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                                  {arch.icon}
                                </div>
                                <div>
                                  <span className="font-medium text-gray-900 text-sm">{arch.name}</span>
                                  <p className="text-xs text-gray-500">{arch.complexity}</p>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* Results Tab */}
          {activeTab === "results" && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                <div>
                  <h2 className="text-2xl font-semibold text-gray-900">Comparison Results</h2>
                  <p className="text-gray-600">Compare outputs from different RAG architectures</p>
                </div>
                {results && (
                  <Badge variant="outline" className="self-start sm:self-auto">
                    Total: {results.total_processing_time.toFixed(2)}s
                  </Badge>
                )}
              </div>

              {isQuerying ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {selectedArchitectures.map((archId, index) => {
                    const arch = architectures.find((a) => a.id === archId)
                    if (!arch) return null
                    return (
                      <motion.div
                        key={archId}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * index }}
                      >
                        <Card>
                          <div className="p-6">
                            <div className="flex items-center space-x-3 mb-4">
                              <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                                {arch.icon}
                              </div>
                              <h3 className="font-medium text-gray-900">{arch.name}</h3>
                            </div>
                            <div className="animate-pulse space-y-3">
                              <div className="h-3 bg-gray-200 rounded w-3/4" />
                              <div className="h-3 bg-gray-200 rounded w-full" />
                              <div className="h-3 bg-gray-200 rounded w-5/6" />
                            </div>
                            <div className="mt-4 flex items-center space-x-2 text-blue-600">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span className="text-sm">Processing...</span>
                            </div>
                          </div>
                        </Card>
                      </motion.div>
                    )
                  })}
                </div>
              ) : results && results.results.length > 0 ? (
                <div className="space-y-6">
                  {/* Performance Overview */}
                  <Card>
                    <div className="p-6">
                      <h3 className="font-medium text-gray-900 mb-4">Performance Overview</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {results.results.map((result) => {
                          const arch = architectures.find((a) => a.id === result.architecture)
                          if (!arch) return null
                          return (
                            <div
                              key={result.architecture}
                              className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200"
                            >
                              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                                {arch.icon}
                              </div>
                              <h4 className="font-medium text-gray-900 mb-2">{arch.name}</h4>
                              <div className="space-y-1 text-sm text-gray-600">
                                <div className="flex items-center justify-center space-x-2">
                                  <Clock className="w-3 h-3" />
                                  <span>{result.processing_time.toFixed(2)}s</span>
                                </div>
                                <div className="flex items-center justify-center space-x-2">
                                  <FileText className="w-3 h-3" />
                                  <span>{result.context.length} chunks</span>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  </Card>

                  {/* Detailed Results */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {results.results.map((result) => {
                      const arch = architectures.find((a) => a.id === result.architecture)
                      if (!arch) return null
                      return (
                        <Card key={result.architecture}>
                          {/* Header */}
                          <div className="p-4 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                                  {arch.icon}
                                </div>
                                <div>
                                  <h3 className="font-medium text-gray-900">{arch.name}</h3>
                                  <Badge variant="outline" className="text-xs">
                                    {arch.complexity}
                                  </Badge>
                                </div>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => copyToClipboard(result.response)}
                                className="text-gray-400 hover:text-gray-600"
                              >
                                <Copy className="w-4 h-4" />
                              </Button>
                            </div>

                            {/* Metadata */}
                            <div className="mt-3 grid grid-cols-2 gap-3 text-sm text-gray-600">
                              <div className="flex items-center space-x-2">
                                <Clock className="w-3 h-3" />
                                <span>{result.processing_time.toFixed(2)}s</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <FileText className="w-3 h-3" />
                                <span>{result.context.length} chunks</span>
                              </div>
                            </div>
                          </div>

                          {/* Response */}
                          <div className="p-4 border-b border-gray-200">
                            <h4 className="font-medium text-gray-900 mb-3">Response</h4>
                            <p className="text-gray-700 text-sm leading-relaxed">{result.response}</p>
                          </div>

                          {/* Context */}
                          <div className="p-4">
                            <h4 className="font-medium text-gray-900 mb-3">Retrieved Context</h4>
                            <div className="space-y-3 max-h-48 overflow-y-auto">
                              {result.context.map((chunk, chunkIndex) => (
                                <div key={chunkIndex} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                                  <p className="text-sm text-gray-700 mb-2 leading-relaxed">
                                    {chunk.page_content || chunk.content || JSON.stringify(chunk)}
                                  </p>
                                  {chunk.metadata && (
                                    <div className="flex items-center justify-between text-xs text-gray-500">
                                      <span>
                                        {chunk.metadata.source && `${chunk.metadata.source}`}
                                        {chunk.metadata.page && ` (Page ${chunk.metadata.page})`}
                                      </span>
                                      {chunk.metadata.score && <span>Score: {chunk.metadata.score}</span>}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        </Card>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Yet</h3>
                  <p className="text-gray-600 mb-6">Submit a query to see comparison results</p>
                  <Button onClick={() => setActiveTab("query")} className="bg-gray-900 hover:bg-gray-800 text-white">
                    Start Querying
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
