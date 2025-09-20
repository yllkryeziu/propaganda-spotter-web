import { useState, useCallback } from "react";
import { Upload, ImageIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ImageUploadProps {
  onImageUpload: (file: File) => void;
  uploadedImage: string | null;
  onClearImage: () => void;
}

export const ImageUpload = ({ onImageUpload, uploadedImage, onClearImage }: ImageUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const imageFile = files.find(file => file.type.startsWith('image/'));
    
    if (imageFile) {
      onImageUpload(imageFile);
    }
  }, [onImageUpload]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  }, [onImageUpload]);

  if (uploadedImage) {
    return (
      <Card className="p-4 border-border bg-card shadow-soft">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-foreground">Uploaded Image</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearImage}
            className="h-8 w-8 p-0 hover:bg-secondary"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="relative">
          <img
            src={uploadedImage}
            alt="Uploaded content"
            className="w-full h-32 object-cover rounded-md border border-border"
          />
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 border-border bg-card shadow-soft">
      <h3 className="text-sm font-medium text-foreground mb-3">Upload Image</h3>
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary/50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <ImageIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-sm text-muted-foreground mb-4">
          Drag and drop an image here, or click to select
        </p>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileInput}
          className="hidden"
          id="image-upload"
        />
        <label htmlFor="image-upload">
          <Button variant="secondary" className="cursor-pointer" asChild>
            <span>
              <Upload className="h-4 w-4 mr-2" />
              Choose Image
            </span>
          </Button>
        </label>
      </div>
    </Card>
  );
};