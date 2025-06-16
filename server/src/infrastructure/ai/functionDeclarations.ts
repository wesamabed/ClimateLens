import { FunctionDeclaration, Type } from '@google/genai';

export const getEmissionsFunction: FunctionDeclaration = {
  name: 'get_emissions',
  description: 'Fetch CO₂ emissions for a country and year or year range.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      country: {
        type: Type.STRING,
        description: 'ISO3 code or full country name.',
      },
      startYear: {
        type: Type.INTEGER,
        description: '4-digit start year.',
      },
      endYear: {
        type: Type.INTEGER,
        description: '4-digit end year (optional).',
      },
    },
    required: ['country', 'startYear'],
  },
};

export const getReportFunction: FunctionDeclaration = {
  name: 'get_report',
  description:
    'Retrieve IPCC report paragraphs by keyword; uses reports collection for transparent citations.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      topic: {
        type: Type.STRING,
        description: 'Keyword or phrase to search in IPCC report text chunks.',
      },
      k: {
        type: Type.INTEGER,
        description: 'Number of paragraphs to return (default 3).',
      },
    },
    required: ['topic'],
  },
};

export const getMaxEmissionsFunction: FunctionDeclaration = {
  name: 'get_max_emissions',
  description: 'Find the country with highest CO₂ emissions in a given year.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      year: {
        type: Type.INTEGER,
        description: '4-digit year to query.',
      },
    },
    required: ['year'],
  },
};

export const getMinEmissionsFunction: FunctionDeclaration = {
  name: 'get_min_emissions',
  description: 'Find the country with lowest CO₂ emissions in a given year.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      year: {
        type: Type.INTEGER,
        description: '4-digit year to query.',
      },
    },
    required: ['year'],
  },
};

export const getAvgEmissionsFunction: FunctionDeclaration = {
  name: 'get_avg_emissions',
  description:
    'Compute average CO₂ emissions for a country over a year range.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      country: {
        type: Type.STRING,
        description: 'ISO3 code or full country name.',
      },
      startYear: {
        type: Type.INTEGER,
        description: '4-digit start year.',
      },
      endYear: {
        type: Type.INTEGER,
        description: '4-digit end year.',
      },
    },
    required: ['country', 'startYear', 'endYear'],
  },
};

export const getTopEmittersFunction: FunctionDeclaration = {
  name: 'get_top_emitters',
  description: 'List the top k CO₂ emitting countries in a given year.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      year: {
        type: Type.INTEGER,
        description: '4-digit year to query.',
      },
      k: {
        type: Type.INTEGER,
        description: 'Number of top countries to return (default 5).',
      },
    },
    required: ['year'],
  },
};

export const getCumulativeEmissionsFunction: FunctionDeclaration = {
  name: 'get_cumulative_emissions',
  description:
    'Sum CO₂ emissions for a country/region from 1850 up to a given end year.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      country: {
        type: Type.STRING,
        description: 'Full country or region name, or ISO3 code.',
      },
      endYear: {
        type: Type.INTEGER,
        description: '4-digit end year (must be ≥1850).',
      },
    },
    required: ['country', 'endYear'],
  },
};

export const getWeatherFunction: FunctionDeclaration = {
  name: 'get_weather',
  description: 'Fetch daily weather (YYYY-MM-DD) or annual summary (YYYY) for a place.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      place: {
        type: Type.STRING,
        description: 'City or station name (e.g. "Paris").',
      },
      date: {
        type: Type.STRING,
        description: 'Exact date YYYY-MM-DD for daily lookup.',
      },
      year: {
        type: Type.INTEGER,
        description: '4-digit year for annual summary.',
      },
    },
    required: ['place'], // date or year is conditionally handled in code
  },
};
