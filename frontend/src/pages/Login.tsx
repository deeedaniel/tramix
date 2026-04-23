import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";
import { API_BASE_URL } from "../config";

export default function Login() {
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem("token")) {
      navigate("/search");
    }
  }, [navigate]);

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) return;

    try {
      const res = await fetch(`${API_BASE_URL}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: credentialResponse.credential }),
      });

      if (!res.ok) throw new Error("Auth failed");

      const data = await res.json();
      localStorage.setItem("token", data.token);
      navigate("/search");
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-xs flex flex-col items-center gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            tramix
          </h1>
          <p className="text-sm text-neutral-500 mt-1">
            find songs that mix well together
          </p>
        </div>
        <GoogleLogin
          onSuccess={handleSuccess}
          onError={() => console.error("Google login failed")}
          theme="filled_black"
          shape="pill"
          text="signin_with"
        />
      </div>
    </div>
  );
}
