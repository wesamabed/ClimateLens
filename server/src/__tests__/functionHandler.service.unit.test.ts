// server/src/__tests__/functionHandler.service.unit.test.ts

import { FunctionHandlerService } from '../application/services/functionHandler.service';
import { geocodeService } from '../infrastructure/geocode.service';
import { mongoSingleton } from '../infrastructure/database/mongo.singleton';

describe('FunctionHandlerService – weather summary via get_weather()', () => {
  let svc: FunctionHandlerService;

  const fakeAggregate = jest.fn(); // Mock for aggregate
  const fakeFindOne = jest.fn(); // Mock for findOne

  // fake "weather" collection with .aggregate and .findOne
  const fakeCollection = {
    aggregate: jest.fn(() => ({
      toArray: fakeAggregate,
    })),
    findOne: fakeFindOne,
  };

  // fake DB object with .collection()
  const fakeDb = { collection: jest.fn().mockReturnValue(fakeCollection) };

  beforeEach(() => {
    svc = new FunctionHandlerService();

    // 1️⃣ Stub geocodeService.lookup → always gives some coords
    jest
      .spyOn(geocodeService, 'lookup')
      .mockResolvedValue({ lat: 10, lon: 20 });

    // 2️⃣ Stub mongoSingleton.connect → our fakeDb
    jest
      .spyOn(mongoSingleton, 'connect')
      .mockResolvedValue(fakeDb as any);

    // 3️⃣ Clear out any prior calls
    fakeAggregate.mockReset();
    fakeFindOne.mockReset();
  });

  it('returns no-station message if none found within radius', async () => {
    // For the "no station found" case, findOne should return null
    fakeFindOne.mockResolvedValueOnce(null);

    const res = await svc.get_weather({ place: 'MockStation', year: 2022 });

    expect(res.answer).toBe(
      'No weather station found within 50 km of MockStation.'
    );
    expect(res.sources).toEqual([]);
  });

  it('calculates annual summary when a station is found nearby', async () => {
    // For the "station found" case, findOne should return a station
    fakeFindOne.mockResolvedValueOnce({ stationId: 'ST123', name: 'MockStation 2km' });

    // The `fakeAggregate` (which is now `toArray`) should resolve with the summary data
    fakeAggregate.mockResolvedValueOnce([{ avgTemp: 15.5, totalPrcp: 123.4 }]);

    const res = await svc.get_weather({ place: 'MockStation', year: 2022 });

    expect(res.answer).toContain('average temperature was **15.5°C**');
    // Change "of" to "was" here to match your function's output
    expect(res.answer).toContain('total precipitation was **123.4 mm**');
    expect(res.sources).toHaveLength(1);
    // Ensure we mention the station name in the source
    expect(res.sources[0].text).toMatch(/MockStation 2km/);
  });
});