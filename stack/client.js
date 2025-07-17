import { StackClientApp } from "@stackframe/js";

export const stackClientApp = new StackClientApp({
  projectId: process.env.BRIDGIT_AI_071625_STACK_PROJECT_ID,
  publishableClientKey: process.env.BRIDGIT_AI_071625_STACK_PUBLISHABLE_CLIENT_KEY,
  tokenStore: "cookie"
});
