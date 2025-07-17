import { StackServerApp } from "@stackframe/js";

export const stackServerApp = new StackServerApp({
  projectId: process.env.BRIDGIT_AI_071625_STACK_PROJECT_ID,
  publishableClientKey: process.env.BRIDGIT_AI_071625_STACK_PUBLISHABLE_CLIENT_KEY,
  secretServerKey: process.env.BRIDGIT_AI_071625_STACK_SECRET_SERVER_KEY,
  tokenStore: "memory"
});
