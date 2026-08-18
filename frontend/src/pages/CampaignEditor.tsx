import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { toast } from "sonner"
import { ArrowLeft, Save, Send } from "lucide-react"
import { Link } from "react-router-dom"
import ReactQuill from "react-quill-new"
import "react-quill-new/dist/quill.snow.css"

export default function CampaignEditor() {
  const [formData, setFormData] = useState({
    title: "",
    subject: "",
    preview_text: "",
    html_content: "<p>Hello {{first_name}},</p><p><br></p><p>Welcome to our latest newsletter!</p>"
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleEditorChange = (content: string) => {
    setFormData({ ...formData, html_content: content })
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Wrap HTML from Quill into a basic MJML structure
    const mjmlContent = `
      <mjml>
        <mj-body>
          <mj-section>
            <mj-column>
              <mj-text>${formData.html_content}</mj-text>
            </mj-column>
          </mj-section>
        </mj-body>
      </mjml>
    `;

    const payload = {
      title: formData.title || "Untitled",
      subject: formData.subject || "No Subject",
      preview_text: formData.preview_text,
      mjml_content: mjmlContent
    };

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/campaigns`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to save campaign");
      toast.success("Campaign saved as draft");
      // Optional: redirect to campaigns list
      window.location.href = "/campaigns";
    } catch (err: any) {
      toast.error(err.message);
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/campaigns">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">New Campaign</h1>
        </div>
        <div className="space-x-2">
          <Button variant="outline" onClick={handleSave}>
            <Save className="mr-2 h-4 w-4" /> Save Draft
          </Button>
          <Button>
            <Send className="mr-2 h-4 w-4" /> Queue for Sending
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Campaign Details</CardTitle>
          <CardDescription>Setup your email metadata</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="title">Internal Title</Label>
            <Input id="title" name="title" value={formData.title} onChange={handleChange} placeholder="e.g. August Newsletter" />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="subject">Email Subject</Label>
            <Input id="subject" name="subject" value={formData.subject} onChange={handleChange} placeholder="Check out our latest news!" />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="preview_text">Preview Text</Label>
            <Input id="preview_text" name="preview_text" value={formData.preview_text} onChange={handleChange} placeholder="Brief summary shown in email client" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Email Content</CardTitle>
          <CardDescription>Design your email using the visual editor</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-white rounded-md">
            <ReactQuill 
              theme="snow" 
              value={formData.html_content} 
              onChange={handleEditorChange} 
              className="h-[350px] mb-12"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
