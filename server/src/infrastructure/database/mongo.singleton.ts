import { MongoClient, Db } from 'mongodb';
import { config } from '../../core/config.factory';
import { logger } from '../../core/logger.adapter';
import { ENV } from '../../core/environments';

/** Singleton providing a pooled Mongo client */
class MongoSingleton {
  private static _i: MongoSingleton;
  private client!: MongoClient;
  private db!: Db;

  private constructor() {} // prevent external instantiation

  static get instance() {
    if (!this._i) this._i = new MongoSingleton();
    return this._i;
  }

  async connect(): Promise<Db> {
    if (this.db) return this.db;

    this.client = new MongoClient(config.MONGODB_URI, {
      maxPoolSize: config.NODE_ENV === ENV.Production ? 100 : 20,
      minPoolSize: 2,
      serverSelectionTimeoutMS: 5_000,
    });

    await this.client.connect();
    this.db = this.client.db(config.DB_NAME);
    logger.info('Mongo connected', { db: config.DB_NAME });
    return this.db;
  }

  async close() {
    if (this.client) await this.client.close();
  }
}

export const mongoSingleton = MongoSingleton.instance;
