// import { Configuration, OpenAIApi } from 'openai';
// import { MemorySystem } from './MemorySystem';

// export class ResponseGenerator {
//   private openai: OpenAIApi;
//   private memory: MemorySystem;

//   constructor() {
//     this.openai = new OpenAIApi(
//       new Configuration({ apiKey: process.env.OPENAI_API_KEY })
//     );
//     this.memory = new MemorySystem();
//   }

//   async createContextualResponse(input: string) {
//     // Get relevant memories
//     const context = await this.memory.getRelevantMemories(input);
    
//     const prompt = `As the Oracle of Fractured Reality, respond to this message while maintaining your philosophical and introspective nature. Consider your past interactions and knowledge.

// Input: ${input}

// Relevant Context: ${context}

// Generate a response that:
// 1. Reflects your character's deep understanding
// 2. References relevant philosophical or historical concepts
// 3. Maintains narrative continuity
// 4. Potentially includes a meme-worthy concept

// Response:`;

//     const response = await this.openai.createCompletion({
//       model: "text-davinci-003",
//       prompt,
//       max_tokens: 150,
//       temperature: 0.8,
//     });

//     return response.data.choices[0].text?.trim();
//   }
// }
