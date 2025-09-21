import { useState, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface HighlightBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  color: string;
}

interface ImageAnalysisProps {
  imageUrl: string | null;
  highlightBoxes: HighlightBox[];
  analysisText: string;
}

export const ImageAnalysis = ({ 
  imageUrl, 
  highlightBoxes, 
  analysisText, 
}: ImageAnalysisProps) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (imageRef.current) {
        const rect = imageRef.current.getBoundingClientRect();
        setImageDimensions({ width: rect.width, height: rect.height });
      }
    };

    if (imageLoaded) {
      updateDimensions();
      window.addEventListener('resize', updateDimensions);
      return () => window.removeEventListener('resize', updateDimensions);
    }
  }, [imageLoaded]);

  const handleImageLoad = () => {
    setImageLoaded(true);
  };


  if (!imageUrl) {
    return (
      <Card className="flex-1 p-8 border-border bg-card shadow-soft">
        <div className="flex items-center justify-center h-full text-center">
            {/* Placeholder content */}
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex-1 flex flex-col border-border bg-card shadow-soft">
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-medium text-foreground">Image Analysis</h3>
      </div>
      
      <div className="flex-1 flex flex-col">
        <div className="relative">
          <img
            ref={imageRef}
            src={imageUrl}
            alt="Analysis subject"
            className="w-full h-auto max-h-[600px] object-contain"
            onLoad={handleImageLoad}
          />
          
          {imageLoaded && highlightBoxes.map((box) => (
            <div
              key={box.id}
              className="absolute border-2 pointer-events-none"
              style={{
                left: `${(box.x / 100) * imageDimensions.width}px`,
                top: `${(box.y / 100) * imageDimensions.height}px`,
                width: `${(box.width / 100) * imageDimensions.width}px`,
                height: `${(box.height / 100) * imageDimensions.height}px`,
                borderColor: box.color,
                backgroundColor: `${box.color}20`,
              }}
            >
              <Badge
                className="absolute -top-7 left-0 text-xs"
                style={{ backgroundColor: box.color, color: 'white' }}
              >
                {box.label}
              </Badge>
            </div>
          ))}
        </div>

        {analysisText && (
          <div className="p-4 border-t border-border">
            <h4 className="text-sm font-medium text-foreground mb-3">Analysis Results</h4>
            <div className="prose prose-sm max-w-none text-foreground leading-relaxed">
              <ReactMarkdown>{analysisText}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};