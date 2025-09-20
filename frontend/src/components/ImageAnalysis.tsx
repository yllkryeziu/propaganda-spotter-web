import { useState, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';
import { Rnd } from "react-rnd";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

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
  setHighlightBoxes: (boxes: HighlightBox[]) => void;
  analysisText: string;
}

export const ImageAnalysis = ({ 
  imageUrl, 
  highlightBoxes, 
  setHighlightBoxes,
  analysisText, 
}: ImageAnalysisProps) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [editingLabel, setEditingLabel] = useState<string | null>(null);
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

  const handleLabelChange = (boxId: string, newLabel: string) => {
    const updatedBoxes = highlightBoxes.map(box => 
      box.id === boxId ? { ...box, label: newLabel } : box
    );
    setHighlightBoxes(updatedBoxes);
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
          
          {imageLoaded && highlightBoxes.map((box, index) => (
            <Rnd
              key={box.id}
              size={{
                width: (box.width / 100) * imageDimensions.width,
                height: (box.height / 100) * imageDimensions.height,
              }}
              position={{
                x: (box.x / 100) * imageDimensions.width,
                y: (box.y / 100) * imageDimensions.height,
              }}
              onDragStop={(e, d) => {
                const newBoxes = [...highlightBoxes];
                newBoxes[index] = {
                  ...newBoxes[index],
                  x: (d.x / imageDimensions.width) * 100,
                  y: (d.y / imageDimensions.height) * 100,
                };
                setHighlightBoxes(newBoxes);
              }}
              onResizeStop={(e, direction, ref, delta, position) => {
                const newBoxes = [...highlightBoxes];
                newBoxes[index] = {
                  ...newBoxes[index],
                  width: (parseFloat(ref.style.width) / imageDimensions.width) * 100,
                  height: (parseFloat(ref.style.height) / imageDimensions.height) * 100,
                  x: (position.x / imageDimensions.width) * 100,
                  y: (position.y / imageDimensions.height) * 100,
                };
                setHighlightBoxes(newBoxes);
              }}
              className="border-2"
              style={{ borderColor: box.color, backgroundColor: `${box.color}20` }}
            >
              <div onDoubleClick={() => setEditingLabel(box.id)} className="w-full h-full">
                {editingLabel === box.id ? (
                  <Input
                    type="text"
                    defaultValue={box.label}
                    className="bg-white/80 text-black text-xs p-1"
                    onBlur={(e) => {
                      handleLabelChange(box.id, e.target.value);
                      setEditingLabel(null);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleLabelChange(box.id, e.currentTarget.value);
                        setEditingLabel(null);
                      }
                    }}
                    autoFocus
                  />
                ) : (
                  <Badge
                    className="absolute -top-7 left-0 text-xs cursor-pointer"
                    style={{ backgroundColor: box.color, color: 'white' }}
                  >
                    {box.label}
                  </Badge>
                )}
              </div>
            </Rnd>
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