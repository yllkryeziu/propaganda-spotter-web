import { useState, useRef, useEffect } from "react";
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
  highlightedWords: Array<{ word: string; id: string; color: string }>;
}

export const ImageAnalysis = ({ 
  imageUrl, 
  highlightBoxes, 
  analysisText, 
  highlightedWords 
}: ImageAnalysisProps) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const imageRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (imageRef.current && imageLoaded) {
      const updateDimensions = () => {
        if (imageRef.current) {
          const rect = imageRef.current.getBoundingClientRect();
          setImageDimensions({ width: rect.width, height: rect.height });
        }
      };

      updateDimensions();
      window.addEventListener('resize', updateDimensions);
      return () => window.removeEventListener('resize', updateDimensions);
    }
  }, [imageLoaded]);

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const renderHighlightedText = (text: string) => {
    if (!highlightedWords.length) return text;

    let result = text;
    highlightedWords.forEach(({ word, id, color }) => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      result = result.replace(
        regex,
        `<mark data-id="${id}" style="background-color: ${color}; color: white; padding: 2px 4px; border-radius: 4px;">${word}</mark>`
      );
    });

    return result;
  };

  if (!imageUrl) {
    return (
      <Card className="flex-1 p-8 border-border bg-card shadow-soft">
        <div className="flex items-center justify-center h-full text-center">
          <div>
            <div className="w-24 h-24 bg-muted rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-12 h-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">Upload an Image</h3>
            <p className="text-muted-foreground">
              Upload an image to start analyzing propaganda elements
            </p>
          </div>
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
        {/* Image with overlay */}
        <div className="relative" ref={containerRef}>
          <img
            ref={imageRef}
            src={imageUrl}
            alt="Analysis subject"
            className="w-full h-auto max-h-[400px] object-contain"
            onLoad={handleImageLoad}
          />
          
          {/* Highlight overlays */}
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
                className="absolute -top-6 left-0 text-xs"
                style={{
                  backgroundColor: box.color,
                  color: 'white',
                }}
              >
                {box.label}
              </Badge>
            </div>
          ))}
        </div>

        {/* Analysis text */}
        {analysisText && (
          <div className="p-4 border-t border-border">
            <h4 className="text-sm font-medium text-foreground mb-3">Analysis Results</h4>
            <div 
              className="text-sm text-foreground leading-relaxed"
              dangerouslySetInnerHTML={{ 
                __html: renderHighlightedText(analysisText) 
              }}
            />
          </div>
        )}
      </div>
    </Card>
  );
};