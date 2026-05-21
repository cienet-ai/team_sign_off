import client from "./client";
import type { User } from "@/types";

export async function getMe(): Promise<User> {
  const resp = await client.get("/auth/me");
  return resp.data;
}

export async function getUsers(): Promise<User[]> {
  const resp = await client.get("/users");
  return resp.data;
}