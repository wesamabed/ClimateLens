// server/src/application/services/functionHandler.service.ts

import { mongoSingleton } from '../../infrastructure/database/mongo.singleton';
import { Source } from './ask.service';
import { embeddingClient } from '../../infrastructure/ai/embedding.client';
import { logger } from '../../core/logger.adapter';
import { geocodeService } from '../../infrastructure/geocode.service';
export interface FunctionResult {
  answer: string;
  sources: Source[];
}

interface EmissionRecord {
  _id: unknown;       // could be ObjectId
  year: number;
  country: string;
  iso3?: string;
  co2Mt: number;
}

interface ReportChunk {
  _id: unknown;
  section: string;
  paragraph: number;
  text: string;
}

export class FunctionHandlerService {
  /** Two-phase emission lookup (exact → fuzzy) */
  async get_emissions(args: {
    country: string;
    startYear: number;
    endYear?: number;
  }): Promise<FunctionResult> {
    const { country, startYear, endYear = startYear } = args;
    const db = await mongoSingleton.connect();

    // 1) Exact-match on country/iso3
    const exactFilter = {
      year: { $gte: startYear, $lte: endYear },
      $or: [
        { country: new RegExp(`^${country}$`, 'i') },
        { iso3:    new RegExp(`^${country}$`, 'i') },
      ],
    };
    let docs = (await db
      .collection<EmissionRecord>('emissions')
      .find(exactFilter)
      .sort({ year: 1 })
      .toArray()) as EmissionRecord[];

    // 2) Fuzzy Atlas Search fallback
    if (docs.length === 0) {
      const pipeline = [
        {
          $search: {
            index: 'emissions_search',
            text: {
              query: country,
              path: ['country', 'iso3'],
              fuzzy: { maxEdits: 2 },
            },
          },
        },
        { $match: { year: { $gte: startYear, $lte: endYear } } },
        { $sort: { year: 1 } },
        { $limit: 1000 },
        { $project: { _id: 1, year: 1, country: 1, co2Mt: 1 } },
      ];
      docs = (await db
        .collection<EmissionRecord>('emissions')
        .aggregate(pipeline)
        .toArray()) as EmissionRecord[];
    }

    if (docs.length === 0) {
      return {
        answer: `No emissions data found for “${country}” in ${startYear}${
          endYear !== startYear ? `–${endYear}` : ''
        }.`,
        sources: [],
      };
    }

    // Numeric summary
    const first = docs[0].co2Mt;
    const last  = docs[docs.length - 1].co2Mt;
    let answer: string;
    if (startYear === endYear && docs.length > 1) {
      const total = docs.reduce((sum, d) => sum + d.co2Mt, 0);
      const answer = `In ${startYear}, ${country} emitted ${total.toFixed(2)} Mt CO₂ (sum of ${docs
        .map((d) => d.country)
        .join(' + ')}).`;
      const sources = docs.map((d) => ({
        id: String(d._id),
        text: `Year ${d.year}: ${d.co2Mt.toFixed(2)} Mt CO₂ (${d.country})`
      }));
      return { answer, sources };
    } else {
      const delta = last - first;
      const span  = (docs[docs.length - 1].year - docs[0].year) || 1;
      const slope = delta / span;
      answer = `Between ${startYear} and ${docs[docs.length - 1].year}, ${docs[0].country}’s CO₂ changed from ${first.toFixed(
        2
      )} to ${last.toFixed(2)} Mt (avg. ${slope.toFixed(2)} Mt/yr).`;
    }

    // Top-3 sources
    const sources: Source[] = docs.slice(0, 3).map((d) => ({
      id: String(d._id),
      text: `Year ${d.year}: ${d.co2Mt.toFixed(2)} Mt CO₂`,
    }));

    return { answer, sources };
  }

  /** Vector kNN on your reports_embedding index */
  async get_report(
    args: { topic: string; k?: number }
  ): Promise<{ answer: string; sources: Source[] }> {
    const { topic, k = 3 } = args;
    const db = await mongoSingleton.connect();

    let hits: ReportChunk[] = [];

    // 1) Try vector search via Atlas Vector Search
    try {
      const queryVector = await embeddingClient.embed(topic);
      const t0 = Date.now();
      hits = (await db
        .collection<ReportChunk>('reports')
        .aggregate([
        {
            $vectorSearch: {
              index: 'reports_embedding',    // your vectorSearch‐type index
              path: 'embedding',             // the field holding embeddings
              queryVector,                   // the raw number[] you got back
              numCandidates: 100,            // how many to scan under the hood
              limit: k,                      // how many results to return
            },
          },
          {
            $project: {
              _id: 1,
              section: 1,
              paragraph: 1,
              text: 1,
              score: { $meta: 'vectorSearchScore' },
            },
          },
        ])
        .toArray()) as ReportChunk[];
    const vectorMs = Date.now() - t0;
    logger.info(`Vector search took ${vectorMs} ms`);
    } catch (err: any) {
      logger.warn(
        'Vector search failed, falling back to full-text Atlas Search',
        { error: err.message || err }
      );

      // 2) Fallback: keyword search via Atlas Search text index
      hits = (await db
        .collection<ReportChunk>('reports')
        .aggregate([
          {
            $search: {
              index: 'reports_text',
              text: {
                query: topic,
                path: 'text',
              },
            },
          },
          { $limit: k },
          {
            $project: {
              _id: 1,
              section: 1,
              paragraph: 1,
              text: 1,
            },
          },
        ])
        .toArray()) as ReportChunk[];
    }

    // 3) Build your result
    if (hits.length === 0) {
      return {
        answer: `No IPCC report paragraphs found for "${topic}".`,
        sources: [],
      };
    }

    const sources: Source[] = hits.map((h, i) => ({
      id: String(h._id),
      text: `[${i + 1}] Section ${h.section}, Para ${h.paragraph}: ${h.text}`,
    }));

    return {
      answer: `Found ${hits.length} relevant report paragraph${
        hits.length > 1 ? 's' : ''
      } for "${topic}".`,
      sources,
    };
  }


  /**
   * Find the country with highest CO₂ emissions in a given year.
   */
  async get_max_emissions(args: { year: number }): Promise<FunctionResult> {
    const { year } = args;
    const db = await mongoSingleton.connect();

    const pipeline = [
      { $match: { year } },
      {
        $group: {
          _id: { country: '$country', iso3: '$iso3' },
          maxCo2: { $max: '$co2Mt' },
        },
      },
      { $sort: { maxCo2: -1 } },
      { $limit: 1 },
      {
        $project: {
          country: '$_id.country',
          iso3: '$_id.iso3',
          maxCo2: 1,
          _id: 0,
        },
      },
    ];

    const [top] = await db.collection('emissions').aggregate(pipeline).toArray();

    if (!top) {
      return { answer: `No emissions data for year ${year}.`, sources: [] };
    }

    const answer = `In ${year}, the highest CO₂ emissions were in ${top.country} (${top.iso3}) at ${top.maxCo2.toFixed(
      2
    )} Mt.`;
    const sources: Source[] = [
      {
        id: `${year}-${top.iso3}-max`,
        text: `Country ${top.country} (${top.iso3}): ${top.maxCo2.toFixed(2)} Mt`,
      },
    ];

    return { answer, sources };
  }

  /**
   * Find the country with lowest CO₂ emissions in a given year.
   */
  async get_min_emissions(args: { year: number }): Promise<FunctionResult> {
    const { year } = args;
    const db = await mongoSingleton.connect();

    const pipeline = [
      { $match: { year } },
      {
        $group: {
          _id: { country: '$country', iso3: '$iso3' },
          minCo2: { $min: '$co2Mt' },
        },
      },
      { $sort: { minCo2: 1 } },
      { $limit: 1 },
      {
        $project: {
          country: '$_id.country',
          iso3: '$_id.iso3',
          minCo2: 1,
          _id: 0,
        },
      },
    ];

    const [bottom] = await db.collection('emissions').aggregate(pipeline).toArray();

    if (!bottom) {
      return { answer: `No emissions data for year ${year}.`, sources: [] };
    }

    const answer = `In ${year}, the lowest CO₂ emissions were in ${bottom.country} (${bottom.iso3}) at ${bottom.minCo2.toFixed(
      2
    )} Mt.`;
    const sources: Source[] = [
      {
        id: `${year}-${bottom.iso3}-min`,
        text: `Country ${bottom.country} (${bottom.iso3}): ${bottom.minCo2.toFixed(2)} Mt`,
      },
    ];

    return { answer, sources };
  }

  /**
   * Compute average CO₂ emissions for a country over a year range.
   */
  async get_avg_emissions(args: {
    country: string;
    startYear: number;
    endYear: number;
  }): Promise<FunctionResult> {
    const { country, startYear, endYear } = args;
    const db = await mongoSingleton.connect();

    const pipeline = [
      {
        $match: {
          year: { $gte: startYear, $lte: endYear },
          $or: [{ country }, { iso3: country }],
        },
      },
      {
        $group: {
          _id: null,
          avgCo2: { $avg: '$co2Mt' },
        },
      },
    ];

    const [res] = await db.collection('emissions').aggregate(pipeline).toArray();

    if (!res) {
      return {
        answer: `No emissions data for ${country} between ${startYear}–${endYear}.`,
        sources: [],
      };
    }

    const answer = `Between ${startYear} and ${endYear}, average CO₂ emissions for ${country} were ${res.avgCo2.toFixed(
      2
    )} Mt.`;
    const sources: Source[] = [
      {
        id: `${country}-${startYear}-${endYear}-avg`,
        text: `Average CO₂: ${res.avgCo2.toFixed(2)} Mt`,
      },
    ];

    return { answer, sources };
  }

  /**
   * List the top k CO₂ emitting countries in a given year.
   */
  async get_top_emitters(args: {
    year: number;
    k?: number;
  }): Promise<FunctionResult> {
    const { year, k = 5 } = args;
    const db = await mongoSingleton.connect();

    const docs = await db
      .collection('emissions')
      .find({ year })
      .sort({ co2Mt: -1 })
      .limit(k)
      .project({ country: 1, iso3: 1, co2Mt: 1 })
      .toArray();

    if (docs.length === 0) {
      return { answer: `No emissions data for year ${year}.`, sources: [] };
    }

    const list = docs
      .map((d, i) => `${i + 1}. ${d.country} (${d.iso3}): ${d.co2Mt.toFixed(2)} Mt`)
      .join('; ');
    const answer = `Top ${k} CO₂ emitters in ${year}: ${list}.`;
    const sources: Source[] = docs.map((d) => ({
      id: `${year}-${d.iso3}`,
      text: `${d.country} (${d.iso3}): ${d.co2Mt.toFixed(2)} Mt`,
    }));

    return { answer, sources };
  }

  async get_cumulative_emissions(args: { country: string; endYear: number }): Promise<FunctionResult> {
    const { country, endYear } = args;
    const db = await mongoSingleton.connect();
    const pipeline = [
      { $match: { year: { $gte: 1850, $lte: endYear }, $or: [{ country: new RegExp(`^${country}$`, 'i') }, { iso3: new RegExp(`^${country}$`, 'i') }] } },
      { $group: { _id: null, totalMt: { $sum: '$co2Mt' } } }
    ];
    const [res] = await db.collection<EmissionRecord>('emissions').aggregate(pipeline).toArray();
    if (!res) {
      return { answer: `No cumulative data for ${country} to ${endYear}.`, sources: [] };
    }
    const totalGt = res.totalMt / 1000;
    const answer = `Cumulative CO₂ from 1850–${endYear} for ${country}: ${totalGt.toFixed(2)} Gt.`;
    const sources = [{
      id: `${country}-${endYear}-cum`,
      text: `Cumulative CO₂: ${totalGt.toFixed(2)} Gt (1850–${endYear})`
    }];
    return { answer, sources };
  }

  async get_weather(args: { place: string; date?: string; year?: number }): Promise<FunctionResult> {
    const { place, date, year } = args;
    // 1) Geocode
    const coords = await geocodeService.lookup(place);
    if (!coords) {
      return { answer: `I couldn’t find coordinates for “${place}.”`, sources: [] };
    }

    const db = await mongoSingleton.connect();
    // 2) Find nearest station within 50 km
    const station = await db.collection('weather').findOne({
      location: {
        $nearSphere: {
          $geometry: {
            type: 'Point',
            coordinates: [coords.lon, coords.lat],
          },
          $maxDistance: 50_000,
        },
      },
    });
    if (!station) {
      return { answer: `No weather station found within 50 km of ${place}.`, sources: [] };
    }

    // 3a) Yearly summary
    if (year !== undefined) {
      const start = new Date(`${year}-01-01T00:00:00Z`);
      const end   = new Date(`${year}-12-31T23:59:59Z`);
      const agg = await db.collection('weather').aggregate([
        { $match: { stationId: station.stationId, recordDate: { $gte: start, $lte: end } } },
        { $group: {
            _id: null,
            avgTemp:   { $avg: '$temp' },
            totalPrcp: { $sum: '$prcp' },
        }},
      ]).toArray();

      if (!agg[0]) {
        return { answer: `No data for ${place} in ${year}.`, sources: [] };
      }
      const { avgTemp, totalPrcp } = agg[0];
      const ans = `In **${year}**, at weather station **${station.name}**, the average temperature was **${avgTemp.toFixed(1)}°C**, and the total precipitation was **${totalPrcp.toFixed(1)} mm**.`;

      return {
        answer: ans,
        sources: [{
          id: `${station.stationId}-${year}-summary`,
          text: `Station ${station.name} (${station.stationId}), ${year}: avgTemp=${avgTemp.toFixed(1)}°C, totalPrcp=${totalPrcp.toFixed(1)} mm`
        }],
      };
    }

    // 3b) Daily lookup
    if (date) {
      const rec = await db.collection('weather').findOne({
        stationId: station.stationId,
        recordDate: new Date(date),
      });
      if (!rec) {
        return { answer: `No data for ${place} on ${date}.`, sources: [] };
      }
      const ans = `On **${date}**, at weather station **${station.name}**, the temperature was **${rec.temp.toFixed(1)}°C**, with a maximum of **${rec.max_temp.toFixed(1)}°C** and a minimum of **${rec.min_temp.toFixed(1)}°C**. Total precipitation for the day was **${rec.prcp.toFixed(1)} mm**.`;
      return {
        answer: ans,
        sources: [{
          id: rec._id.toString(),
          text: `Station ${station.name} (${station.stationId}), ${date}: temp=${rec.temp.toFixed(1)}°C, max=${rec.max_temp.toFixed(1)}°C, min=${rec.min_temp.toFixed(1)}°C, prcp=${rec.prcp.toFixed(1)} mm`
        }],
      };
    }

    // 3c) Neither date nor year
    return {
      answer: 'Please provide either a full date (YYYY-MM-DD) or a year (YYYY).',
      sources: []
    };
  }

  private async get_weather_daily(args: { place: string; date: string }): Promise<FunctionResult> {
    const { place, date } = args;
    const db = await mongoSingleton.connect();
    // fuzzy match station name, then exact date
    const stations = await db.collection('weather')
      .aggregate([
        { $search: { index: 'weather_text', text: { query: place, path: 'name', fuzzy: { maxEdits: 2 } } } },
        { $limit: 1 },
        { $project: { stationId: 1, name: 1 } }
      ]).toArray();
    if (!stations[0]) {
      return { answer: `No weather station found for "${place}".`, sources: [] };
    }
    const station = stations[0];
    const rec = await db.collection('weather').findOne({
      stationId: station.stationId,
      recordDate: new Date(date)
    });
    if (!rec) {
      return { answer: `No data for ${place} on ${date}.`, sources: [] };
    }
    const ans = `On ${new Date(date).toLocaleDateString()}, the weather station ${station.name} recorded an average temperature of ${rec.temp.toFixed(1)}°C, with a maximum of ${rec.max_temp.toFixed(1)}°C and a minimum of ${rec.min_temp.toFixed(1)}°C. Total precipitation for the day was ${rec.prcp.toFixed(1)} mm.`;
    return {
      answer: ans,
      sources: [{
        id: rec._id.toString(),
        text: `Station ${station.name} (${station.stationId}), ${date}: temp=${rec.temp.toFixed(1)}°C, prcp=${rec.prcp.toFixed(1)} mm`
      }],
    };
  }

  private async get_weather_summary(args: { place: string; year: number }): Promise<FunctionResult> {
    const { place, year } = args;
    const db = await mongoSingleton.connect();
    // fuzzy match station name
    const stations = await db.collection('weather')
      .aggregate([
        { $search: { index: 'weather_text', text: { query: place, path: 'name', fuzzy: { maxEdits: 2 } } } },
        { $limit: 1 },
        { $project: { stationId: 1, name: 1 } }
      ]).toArray();
    if (!stations[0]) {
      return { answer: `No weather station found for "${place}".`, sources: [] };
    }
    const station = stations[0];
    // aggregate over the whole year
    const start = new Date(`${year}-01-01T00:00:00Z`);
    const end   = new Date(`${year}-12-31T23:59:59Z`);
    const agg = await db.collection('weather').aggregate([
      { $match: { stationId: station.stationId, recordDate: { $gte: start, $lte: end } } },
      { $group: {
          _id: null,
          avgTemp:   { $avg: '$temp' },
          totalPrcp: { $sum: '$prcp' }
      }}
    ]).toArray();
    if (!agg[0]) {
      return { answer: `No data for ${place} in ${year}.`, sources: [] };
    }
    const { avgTemp, totalPrcp } = agg[0];
    const ans = `In **${year}**, the weather station **${station.name}** recorded an average temperature of **${avgTemp.toFixed(1)}°C**, and a total precipitation of **${totalPrcp.toFixed(1)} mm**.`;

    return {
      answer: ans,
      sources: [{
        id: `${station.stationId}-${year}-summary`,
        text: `Station ${station.name} (${station.stationId}), ${year}: avgTemp=${avgTemp.toFixed(1)}°C, prcp=${totalPrcp.toFixed(1)} mm`
      }],
    };
  }
}

export const functionHandlerService = new FunctionHandlerService();
