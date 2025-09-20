import { useState, useEffect } from "react";
import { ImageUpload } from "@/components/ImageUpload";
import { ImageAnalysis } from "@/components/ImageAnalysis";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";

// API configuration
const API_BASE_URL = "http://localhost:8000";

// Types for API responses
interface BoundingBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  color: string;
  confidence: number;
}

interface HighlightedWord {
  word: string;
  id: string;
  color: string;
}

interface AnalysisResponse {
  success: boolean;
  analysis_text: string;
  bounding_boxes: BoundingBox[];
  highlighted_words: HighlightedWord[];
  confidence_score: number;
  processing_time: number;
  error_message?: string;
}

const Index = () => {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [highlightBoxes, setHighlightBoxes] = useState<BoundingBox[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    if (analysisResult) {
      setHighlightBoxes(analysisResult.bounding_boxes);
    }
  }, [analysisResult]);

  const handleImageUpload = (file: File) => {
    const url = URL.createObjectURL(file);
    setUploadedImage(url);
    setUploadedFile(file);
    setAnalysisResult(null);
    setHighlightBoxes([]);
    toast({
      title: "Image uploaded",
      description: "Your image has been uploaded successfully. Now click analyze to detect propaganda elements!",
    });
  };

  const handleClearImage = () => {
    if (uploadedImage) {
      URL.revokeObjectURL(uploadedImage);
    }
    setUploadedImage(null);
    setUploadedFile(null);
    setAnalysisResult(null);
    setHighlightBoxes([]);
  };

  const handleAnalyzeImage = async () => {
    if (!uploadedFile) {
      toast({
        title: "No image uploaded",
        description: "Please upload an image first before asking for analysis.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setHighlightBoxes([]);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: AnalysisResponse = await response.json();

      if (result.success) {
        setAnalysisResult(result);
      } else {
        throw new Error(result.error_message || "Analysis failed");
      }

    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "Failed to analyze image. Make sure the backend server is running.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card shadow-soft">
        <div className="container mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-foreground">
            Propaganda Analysis Tool
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Upload images and analyze propaganda elements using AI
          </p>
        </div>
      </header>

      <main className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-140px)]">
          <div className="flex flex-col gap-4">
            <ImageUpload
              onImageUpload={handleImageUpload}
              uploadedImage={uploadedImage}
              onClearImage={handleClearImage}
            />
            {uploadedImage && (
              <div className="flex justify-center">
                <Button
                  onClick={handleAnalyzeImage}
                  disabled={isAnalyzing}
                  className="w-full max-w-sm"
                >
                  {isAnalyzing ? "Analyzing..." : "Analyze for Propaganda"}
                </Button>
              </div>
            )}
          </div>

          <ImageAnalysis
            imageUrl={uploadedImage}
            highlightBoxes={highlightBoxes}
            setHighlightBoxes={setHighlightBoxes}
            analysisText={analysisResult ? analysisResult.analysis_text : ""}
          />
        </div>
      </main>
    </div>
  );
};

export default Index;