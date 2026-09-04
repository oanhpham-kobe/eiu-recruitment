export type PublicSupabaseEnv = {
  url: string;
  publishableKey: string;
};

function requirePublicEnvironmentVariable(name: string): string {
  const value = process.env[name]?.trim();

  if (!value) {
    throw new Error(`${name} must be configured`);
  }

  return value;
}

export function getPublicSupabaseEnv(): PublicSupabaseEnv {
  const publishableKey =
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY?.trim() ??
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.trim();

  if (!publishableKey) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY or NEXT_PUBLIC_SUPABASE_ANON_KEY must be configured",
    );
  }

  return {
    url: requirePublicEnvironmentVariable("NEXT_PUBLIC_SUPABASE_URL"),
    publishableKey,
  };
}
