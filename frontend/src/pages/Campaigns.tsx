import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Play, FileEdit } from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"

interface Campaign {
  id: string;
  title: string;
  status: string;
  sent_count: number;
  created_at: string;
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])

  const fetchCampaigns = () => {
    fetch(`${import.meta.env.VITE_API_URL || ''}/api/campaigns`)
      .then(res => res.json())
      .then(data => setCampaigns(data))
      .catch(err => console.error(err))
  }

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const handleLaunch = (id: string) => {
    fetch(`${import.meta.env.VITE_API_URL || ''}/api/campaigns/${id}/launch`, { method: 'POST' })
      .then(res => {
        if (!res.ok) throw new Error("Failed to launch")
        toast.success("Campaign queued for sending!")
        fetchCampaigns()
      })
      .catch(err => toast.error(err.message))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Campaigns</h1>
        <Link to="/campaigns/new">
          <Button>Create Campaign</Button>
        </Link>
      </div>

      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Sent</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {campaigns.map((camp) => (
              <TableRow key={camp.id}>
                <TableCell className="font-medium">{camp.title}</TableCell>
                <TableCell>
                  <Badge variant={camp.status === 'COMPLETED' ? 'default' : camp.status === 'DRAFT' ? 'secondary' : 'outline'}>
                    {camp.status}
                  </Badge>
                </TableCell>
                <TableCell>{camp.sent_count?.toLocaleString()}</TableCell>
                <TableCell>{new Date(camp.created_at).toLocaleDateString()}</TableCell>
                <TableCell className="text-right space-x-2">
                  <Button variant="outline" size="icon">
                    <FileEdit className="h-4 w-4" />
                  </Button>
                  {camp.status === 'DRAFT' && (
                    <Button variant="default" size="icon" onClick={() => handleLaunch(camp.id)}>
                      <Play className="h-4 w-4" />
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
