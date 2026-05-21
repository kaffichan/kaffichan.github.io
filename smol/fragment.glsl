#version 330 core
out vec4 FragColor;
in vec2 TexCoords;
in vec3 WorldPos;
in vec3 Normal;
in vec4 FragPosLightSpace;

uniform sampler2D texture_diffuse;
uniform sampler2D shadowMap;
uniform bool isFloor;
uniform vec3 viewPos;
uniform vec3 lightPos;

float ShadowCalculation(vec4 fragPosLightSpace) {
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projCoords = projCoords * 0.5 + 0.5;
    if(projCoords.z > 1.0) return 0.0;

    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
            float pcfDepth = texture(shadowMap, projCoords.xy + vec2(x, y) * texelSize).r;
            // shadow += projCoords.z - 0.005 > pcfDepth ? 1.0 : 0.0;
            vec3 normal = normalize(Normal);
            vec3 lightDir = normalize(lightPos - WorldPos);
            float bias = max(0.05 * (1.0 - dot(normal, lightDir)), 0.005);
            shadow += projCoords.z - bias > pcfDepth ? 1.0 : 0.0;
        }
    }
    return shadow / 9.0;
}

void main() {
    vec3 color = isFloor ? vec3(0.2) : texture(texture_diffuse, TexCoords).rgb;
    if(isFloor) {
        vec2 uv = WorldPos.xz;
        float pattern = abs(mod(floor(uv.x), 2.0) - mod(floor(uv.y), 2.0));
        color = mix(vec3(0.15), vec3(0.25), pattern);
    }

    vec3 normal = normalize(Normal);
    vec3 lightDir = normalize(lightPos - WorldPos);

    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * vec3(2.0, 2.0, 1.8);

    float distance = length(lightPos - WorldPos);
    float attenuation = 1.0;

    vec3 ambient = vec3(0.1) * color;

    float shadow = ShadowCalculation(FragPosLightSpace);

    vec3 result = (ambient + (1.0 - shadow) * (diffuse * attenuation)) * color;
    // float dist = distance(WorldPos, viewPos);
    // float fog = smoothstep(15.0, 50.0, dist);
    // FragColor = vec4(mix(result, vec3(0.1, 0.2, 0.3), fog), 1.0);
    FragColor = vec4(result, 1.0);
}