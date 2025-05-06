import { QuickSightClient, GenerateEmbedUrlForRegisteredUserCommand } from "@aws-sdk/client-quicksight";

const quicksightClient = new QuickSightClient({ region: "us-east-1" });

// Valores hardcodeados (¡No recomendado para entornos reales!)
const AWS_ACCOUNT_ID = "240435918890";
const QUICKSIGHT_USER_ARN = "arn:aws:quicksight:us-east-1:240435918890:user/default/diego-dev";
const ALLOWED_DOMAIN = "http://d19kpussj440vd.cloudfront.net";
const DASHBOARD_ID = "57aab648-7a18-4f91-9c8a-0d89ffb98823";

export const handler = async (event) => {
  try {
    const params = {
      AwsAccountId: AWS_ACCOUNT_ID,
      UserArn: QUICKSIGHT_USER_ARN,
      SessionLifetimeInMinutes: 600,
      ExperienceConfiguration: {
        Dashboard: {
          InitialDashboardId: DASHBOARD_ID,
        },
      },
      AllowedDomains: [ALLOWED_DOMAIN],
    };

    const command = new GenerateEmbedUrlForRegisteredUserCommand(params);
    const response = await quicksightClient.send(command);

    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": ALLOWED_DOMAIN,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ embedUrl: response.EmbedUrl }),
    };
  } catch (error) {
    console.error("Error:", error);
    return {
      statusCode: 500,
      headers: { "Access-Control-Allow-Origin": ALLOWED_DOMAIN },
      body: JSON.stringify({ error: "Error generando URL" }),
    };
  }
};