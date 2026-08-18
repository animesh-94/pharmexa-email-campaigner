import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Upload, Search, Download } from "lucide-react"
import { useEffect, useState, useRef } from "react"
import { toast } from "sonner"

interface Subscriber {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  bounce_count: number;
}

export default function Subscribers() {
  const [subscribers, setSubscribers] = useState<Subscriber[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const fetchSubscribers = () => {
    fetch(`${import.meta.env.VITE_API_URL || ''}/api/subscribers`)
      .then(res => res.json())
      .then(data => setSubscribers(data))
      .catch(err => console.error("Failed to fetch subscribers:", err))
  }

  useEffect(() => {
    fetchSubscribers()
  }, [])

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append("file", file)

    toast.promise(
      fetch(`${import.meta.env.VITE_API_URL || ''}/api/subscribers/upload`, {
        method: "POST",
        body: formData,
      }).then(async (res) => {
        if (!res.ok) throw new Error("Upload failed")
        const data = await res.json()
        fetchSubscribers()
        return data
      }),
      {
        loading: 'Uploading CSV...',
        success: (data) => `Successfully imported ${data.inserted} subscribers (${data.skipped} skipped)`,
        error: 'Error uploading CSV',
      }
    )
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Subscribers</h1>
        <div className="space-x-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
          <input 
            type="file" 
            accept=".csv" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            className="hidden" 
          />
          <Button onClick={handleUploadClick}>
            <Upload className="mr-2 h-4 w-4" /> Import CSV
          </Button>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input type="search" placeholder="Search email..." className="pl-8" />
        </div>
      </div>

      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Bounces</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {subscribers.map((sub) => (
              <TableRow key={sub.id}>
                <TableCell className="font-medium">{sub.email}</TableCell>
                <TableCell>{[sub.first_name, sub.last_name].filter(Boolean).join(' ') || "-"}</TableCell>
                <TableCell>
                  {sub.is_active ? (
                    <Badge variant="default" className="bg-green-500 hover:bg-green-600">Active</Badge>
                  ) : (
                    <Badge variant="destructive">Suppressed</Badge>
                  )}
                </TableCell>
                <TableCell>{sub.bounce_count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
