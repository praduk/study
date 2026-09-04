'use client';

/* oxlint-disable jsx-a11y/prefer-tag-over-role, next/no-img-element */
// The dark-mode bitmap is a canvas with image semantics, and authored local
// images must stay native so the same pixels can be copied into that canvas.

import { useEffect, useRef, useState } from 'react';

function rgbToHsl(red: number, green: number, blue: number): [number, number, number] {
  const r = red / 255;
  const g = green / 255;
  const b = blue / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const lightness = (max + min) / 2;
  if (max === min) return [0, 0, lightness];
  const delta = max - min;
  const saturation = lightness > 0.5 ? delta / (2 - max - min) : delta / (max + min);
  let hue = max === r ? (g - b) / delta + (g < b ? 6 : 0) : max === g ? (b - r) / delta + 2 : (r - g) / delta + 4;
  hue /= 6;
  return [hue, saturation, lightness];
}

function hueToRgb(p: number, q: number, value: number): number {
  let t = value;
  if (t < 0) t += 1;
  if (t > 1) t -= 1;
  if (t < 1 / 6) return p + (q - p) * 6 * t;
  if (t < 1 / 2) return q;
  if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
  return p;
}

function hslToRgb(hue: number, saturation: number, lightness: number): [number, number, number] {
  if (saturation === 0) {
    const gray = Math.round(lightness * 255);
    return [gray, gray, gray];
  }
  const q = lightness < 0.5 ? lightness * (1 + saturation) : lightness + saturation - lightness * saturation;
  const p = 2 * lightness - q;
  return [
    Math.round(hueToRgb(p, q, hue + 1 / 3) * 255),
    Math.round(hueToRgb(p, q, hue) * 255),
    Math.round(hueToRgb(p, q, hue - 1 / 3) * 255),
  ];
}

interface LightnessImageProps {
  src: string;
  alt: string;
  widthPercent: number;
  invertLightness: boolean;
}

export function LightnessImage({ src, alt, widthPercent, invertLightness }: LightnessImageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dark, setDark] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const update = () => setDark(document.documentElement.classList.contains('dark'));
    update();
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!dark || !invertLightness) return;
    let cancelled = false;
    const image = new Image();
    image.decoding = 'async';
    image.onload = () => {
      if (cancelled || !canvasRef.current) return;
      const canvas = canvasRef.current;
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) return;
      context.drawImage(image, 0, 0);
      const pixels = context.getImageData(0, 0, canvas.width, canvas.height);
      for (let index = 0; index < pixels.data.length; index += 4) {
        const [h, s, l] = rgbToHsl(pixels.data[index], pixels.data[index + 1], pixels.data[index + 2]);
        const [r, g, b] = hslToRgb(h, s, 1 - l);
        pixels.data[index] = r;
        pixels.data[index + 1] = g;
        pixels.data[index + 2] = b;
      }
      context.putImageData(pixels, 0, 0);
      setReady(true);
    };
    image.src = src;
    return () => { cancelled = true; };
  }, [dark, invertLightness, src]);

  const style = { width: `${Math.min(100, Math.max(10, widthPercent))}%` };
  if (dark && invertLightness) {
    return (
      <figure className="content-image" style={style}>
        <canvas ref={canvasRef} aria-label={alt} role="img" className={ready ? '' : 'image-loading'} />
      </figure>
    );
  }
  return <img className="content-image" src={src} alt={alt} style={style} loading="lazy" />;
}
