import { QuickSightClient, GenerateEmbedUrlForRegisteredUserCommand } from "@aws-sdk/client-quicksight";

const quicksightClient = new QuickSightClient({ region: "us-east-1" });

export const handler = async (event) => {
  try {
    const params = {
      AwsAccountId: "240435918890",
      UserArn: "arn:aws:quicksight:us-east-1:240435918890:user/default/diego-dev",
      SessionLifetimeInMinutes: 600,
      ExperienceConfiguration: {
        Dashboard: {
          InitialDashboardId: "57aab648-7a18-4f91-9c8a-0d89ffb98823",  // Tu ID de dashboard
        },
      },
      AllowedDomains: [process.env.ALLOWED_DOMAIN],
    };

    const command = new GenerateEmbedUrlForRegisteredUserCommand(params);
    const response = await quicksightClient.send(command);

    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": process.env.ALLOWED_DOMAIN,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ embedUrl: response.EmbedUrl }),
    };
  } catch (error) {
    console.error("Error:", error);
    return {
      statusCode: 500,
      headers: { "Access-Control-Allow-Origin": process.env.ALLOWED_DOMAIN },
      body: JSON.stringify({ error: "Error generando URL" }),
    };
  }
};