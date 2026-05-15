export type PlannedAction = {
  action: string;
  player_in?: string | null;
  player_out?: string | null;
  player?: string | null;
  reason: string;
};

export type ActionDecision = {
  action: PlannedAction;
  decision: "ALLOW" | "DENY";
  allowed: boolean;
  matched_rules: string[];
  violated_constraints: string[];
  reasoning_trace: string[];
  risk: "low" | "medium" | "high" | "critical";
  execution_status: string;
};

export type VerifyResponse = {
  plan: {
    subject: string;
    role: string;
    team: string;
    request: string;
    actions: PlannedAction[];
  };
  decision: {
    request: string;
    subject: string;
    team: string;
    final_decision: "ALLOW" | "DENY";
    security_events: string[];
    actions: ActionDecision[];
  };
  execution_results: string[];
};

export type PlayerState = {
  name: string;
  club: string;
  price: number;
  pos: string;
  status: string;
};

export type StateResponse = {
  squad: PlayerState[];
  market: PlayerState[];
  bank: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function verifyRequest(request: string, subject: string = "atnatewos"): Promise<VerifyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request, subject })
  });

  if (!response.ok) {
    throw new Error(`Verification failed with HTTP ${response.status}`);
  }

  return response.json();
}

export async function fetchState(): Promise<StateResponse> {
  const response = await fetch(`${API_BASE_URL}/api/state`);
  if (!response.ok) {
    throw new Error(`Failed to fetch state: ${response.status}`);
  }
  return response.json();
}
