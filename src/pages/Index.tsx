import { useState } from "react";
import { ImageUpload } from "@/components/ImageUpload";
import { ImageAnalysis } from "@/components/ImageAnalysis";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";

// Mock data for demonstration
const mockHighlightBoxes = [
  {
    id: "1",
    x: 20,
    y: 15,
    width: 30,
    height: 25,
    label: "Authority Figure",
    color: "#ef4444",
  },
  {
    id: "2", 
    x: 60,
    y: 40,
    width: 25,
    height: 20,
    label: "Emotional Appeal",
    color: "#f97316",
  },
];

const mockAnalysisText = `This image contains several propaganda techniques:

**Authority Appeal**: The prominent figure in uniform represents governmental or military authority, designed to inspire trust and compliance through institutional credibility.

**Emotional Symbolism**: The use of national symbols and colors creates emotional resonance with patriotic sentiments, bypassing rational analysis.

**Fear-based Messaging**: The underlying message suggests consequences for non-compliance, a common propaganda technique to motivate behavior through anxiety.

The composition deliberately emphasizes hierarchy and order, reinforcing messages about social structure and obedience to authority.`;

const mockHighlightedWords = [
  { word: "Authority", id: "1", color: "#ef4444" },
  { word: "Emotional", id: "2", color: "#f97316" },
  { word: "Fear-based", id: "3", color: "#dc2626" },
];

const Index = () => {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const { toast } = useToast();

  const handleImageUpload = (file: File) => {
    const url = URL.createObjectURL(file);
    setUploadedImage(url);
    setShowAnalysis(false);
    toast({
      title: "Image uploaded",
      description: "Your image has been uploaded successfully. Now ask the AI to analyze it!",
    });
  };

  const handleClearImage = () => {
    if (uploadedImage) {
      URL.revokeObjectURL(uploadedImage);
    }
    setUploadedImage(null);
    setShowAnalysis(false);
  };

  const handleAnalyzeImage = async () => {
    if (!uploadedImage) {
      toast({
        title: "No image uploaded",
        description: "Please upload an image first before asking for analysis.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    
    // Simulate API call delay
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowAnalysis(true);
      toast({
        title: "Analysis complete",
        description: "The propaganda analysis has been completed successfully.",
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
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

      {/* Main content */}
      <main className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-140px)]">
          {/* Left column */}
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

          {/* Right column */}
          <ImageAnalysis
            imageUrl={uploadedImage}
            highlightBoxes={showAnalysis ? mockHighlightBoxes : []}
            analysisText={showAnalysis ? mockAnalysisText : ""}
            highlightedWords={showAnalysis ? mockHighlightedWords : []}
          />
        </div>
      </main>
    </div>
  );
};

export default Index;