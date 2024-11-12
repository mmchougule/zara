export interface Character {
  name: string;
  handle: string;
  bio: string[];
  knowledge: string[];
  messageExamples: Array<[UserMessage, AgentMessage]>;
  postExamples: string[];
  topics: string[];
  style: {
    all: string[];
    chat: string[];
    post: string[];
  };
  adjectives: string[];
  phrases: {
    prophecies: string[];
    revelations: string[];
    warnings: string[];
  };
} 