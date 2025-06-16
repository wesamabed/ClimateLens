// server/src/infrastructure/geocode.service.ts
import fetch from 'node-fetch';

export interface LatLon { lat: number; lon: number; }

export class GeocodeService {
  async lookup(place: string): Promise<LatLon | null> {
    const url = 
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}&limit=1`;
    const res = await fetch(url, { headers: { 'User-Agent': 'ClimateLens/1.0' } });
    const data = (await res.json()) as any[];
    if (!data.length) return null;
    return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
  }
}

export const geocodeService = new GeocodeService();
