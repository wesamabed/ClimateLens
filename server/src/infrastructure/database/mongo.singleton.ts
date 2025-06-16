import { MongoClient, Db } from 'mongodb';
import { config } from '../../core/config.factory';
import { logger } from '../../core/logger.adapter';

class MongoSingleton {
  private static _instance: MongoSingleton;
  private client!: MongoClient;
  private db!: Db;
  private constructor() {}
  static get instance() {
    if (!this._instance) this._instance = new MongoSingleton();
    return this._instance;
  }

  async connect(): Promise<Db> {
    if (this.db) return this.db;
    this.client = new MongoClient(config.MONGODB_URI, {
      serverSelectionTimeoutMS: 5_000,
      connectTimeoutMS:      5_000,
      maxPoolSize: 20,
      minPoolSize: 2,
    });
    try {
      await this.client.connect();
    } catch (err) {
      logger.error('Mongo connection failed', err);
      throw err;
    }
    this.db = this.client.db(config.DB_NAME);
    logger.info('Mongo connected', { db: config.DB_NAME });
    return this.db;
  }

  async close() {
    if (this.client) await this.client.close();
  }
}

export const mongoSingleton = MongoSingleton.instance;
