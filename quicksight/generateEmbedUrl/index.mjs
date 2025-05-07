import { QuickSightClient, GenerateEmbedUrlForRegisteredUserCommand } from "@aws-sdk/client-quicksight";

const quicksightClient = new QuickSightClient({ region: "us-east-1" });

// Valores hardcodeados
const CONFIG = {
  AWS_ACCOUNT_ID: "240435918890",
  QUICKSIGHT_USER_ARN: "arn:aws:quicksight:us-east-1:240435918890:user/default/diego-dev",
  ALLOWED_DOMAIN: "https://d19kpussj440vd.cloudfront.net",
  // DASHBOARD_ID: "57aab648-7a18-4f91-9c8a-0d89ffb98823"
  DASHBOARD_ID: "34c6f29e-da26-4c46-93e9-afe512a5af78"
};

export const handler = async () => { // No necesitas el parámetro 'event'
  try {
    console.log("Iniciando generación de URL...");

    const params = {
      AwsAccountId: CONFIG.AWS_ACCOUNT_ID,
      UserArn: CONFIG.QUICKSIGHT_USER_ARN,
      SessionLifetimeInMinutes: 600,
      ExperienceConfiguration: {
        Dashboard: {
          InitialDashboardId: CONFIG.DASHBOARD_ID
        }
      },
      AllowedDomains: [CONFIG.ALLOWED_DOMAIN]
    };

    console.log("Parámetros:", JSON.stringify(params, null, 2));

    const command = new GenerateEmbedUrlForRegisteredUserCommand(params);
    const response = await quicksightClient.send(command);

    console.log("Respuesta de QuickSight:", response);

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": CONFIG.ALLOWED_DOMAIN,
        "Access-Control-Allow-Methods": "GET"
      },
      body: JSON.stringify({
        embedUrl: response.EmbedUrl
      })
    };

  } catch (error) {
    console.error("Error crítico:", error);
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": CONFIG.ALLOWED_DOMAIN
      },
      body: JSON.stringify({
        error: "Error interno del servidor",
        code: "QS_EMBED_FAIL"
      })
    };
  }
};