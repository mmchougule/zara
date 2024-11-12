// import { MongoClient } from 'mongodb';

// export class MemorySystem {
//   private client: MongoClient;
  
//   constructor() {
//     this.client = new MongoClient(process.env.MONGODB_URI!);
//   }

//   async storeMemory(entry: {
//     content: string;
//     type: 'interaction' | 'insight' | 'meme';
//     timestamp: Date;
//     tags: string[];
//   }) {
//     await this.client.connect();
//     const collection = this.client.db('oracle').collection('memories');
//     await collection.insertOne(entry);
//   }

//   async getRelevantMemories(input: string) {
//     await this.client.connect();
//     const collection = this.client.db('oracle').collection('memories');
    
//     // Use text search to find relevant memories
//     const memories = await collection
//       .find({ $text: { $search: input } })
//       .sort({ timestamp: -1 })
//       .limit(3)
//       .toArray();

//     return memories;
//   }
// }
