#include <iostream>
#include "glad/glad.h"
#include "glfw/glfw3.h"
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <fstream>
#include <sstream>
#include <map>
#include <cstdio>
#include <memory>
#include <thread>
#include <chrono>

std::string readShaderCode(const char* filePath) {
    std::ifstream file(filePath);
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#define TINYOBJLOADER_IMPLEMENTATION
#include "tiny_obj_loader.h"

std::map<std::string, unsigned int> materialTextures;

struct Mesh {
    unsigned int VAO, VBO;
    int vertexCount;
    unsigned int textureID;
};

std::vector<Mesh> sceneMeshes;

struct PlacedObject {
    glm::vec3 position;
    int meshIndex;
};

std::vector<PlacedObject> worldObjects;

unsigned int loadTexture(const char* path) {
    unsigned int textureID;
    glGenTextures(1, &textureID);

    int width, height, nrComponents;
    stbi_set_flip_vertically_on_load(true);
    unsigned char* data = stbi_load(path, &width, &height, &nrComponents, 0);
    if (data) {
        GLenum format = (nrComponents == 4) ? GL_RGBA : GL_RGB;
        glBindTexture(GL_TEXTURE_2D, textureID);
        glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
        glGenerateMipmap(GL_TEXTURE_2D);

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

        stbi_image_free(data);
    } else {
        std::cout << "Texture failed to load at path: " << path << std::endl;
        stbi_image_free(data);
    }
    return textureID;
}

std::string currentModelPath = "";
bool isModelLoaded = false;

void clearCurrentModel() {
    for (auto& mesh : sceneMeshes) {
        glDeleteVertexArrays(1, &mesh.VAO);
        glDeleteBuffers(1, &mesh.VBO);
    }
    sceneMeshes.clear();
    materialTextures.clear();
}

std::string openFilePicker() {
    std::string cmd = "osascript -e 'POSIX path of (choose file with prompt \"Select .obj model\" of type {\"obj\"})' 2>/dev/null";

    char buffer[1024];
    std::string result = "";
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);

    if (pipe && fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
        result = buffer;
        if (!result.empty() && result.back() == '\n') result.pop_back();
    }
    return result;
}

enum class EditMode { MODEL, LIGHT };
EditMode currentMode = EditMode::MODEL;

struct LightSource {
    glm::vec3 position;
    glm::vec3 color = glm::vec3(1.0f, 0.9f, 0.8f);
};

std::vector<LightSource> worldLights;

enum ObjectType { OBJ_MODEL, OBJ_LIGHT };

struct HistoryItem {
    ObjectType type;
};

std::vector<HistoryItem> creationHistory;

// ПАРАМЕТРЫ МИРА:
// Сетка: 1 unit = 1 метр. 
// Плоскость пола: от -25.0 до 25.0 по X и Z.
// Рекомендуемый шаг для размещения объектов: 1.0f.

const unsigned int SCR_WIDTH = 800;
const unsigned int SCR_HEIGHT = 600;

float cameraPos[3] = {0.0f, 0.0f, 3.0f};
float cameraSpeed = 2.5f;
float deltaTime = 0.0f;
float lastFrame = 0.0f;

float velocityY = 0.0f;
bool isGrounded = true;
const float GRAVITY = -9.8f;

bool firstMouse = true;
float yaw = -90.0f;
float pitch = 0.0f;
float lastX = SCR_WIDTH / 2.0f;
float lastY = SCR_HEIGHT / 2.0f;

glm::vec3 cameraFront = glm::vec3(0.0f, 0.0f, -1.0f);

bool loadModel(const std::string& objPath) {
    tinyobj::attrib_t attrib;
    std::vector<tinyobj::shape_t> shapes;
    std::vector<tinyobj::material_t> materials;
    std::string err;

    std::string baseDir = objPath.substr(0, objPath.find_last_of("/\\") + 1);

    bool ret = tinyobj::LoadObj(&attrib, &shapes, &materials, &err, objPath.c_str(), baseDir.c_str(), true);
    if (!ret) return false;

    for (const auto& mat : materials) {
        if (!mat.diffuse_texname.empty()) {
            std::string fullTexPath = baseDir + mat.diffuse_texname;

            if (materialTextures.find(mat.name) == materialTextures.end()) {
                materialTextures[mat.name] = loadTexture(fullTexPath.c_str());
            }
        }
    }
    
    for (const auto& shape : shapes) {
        std::vector<float> vertices;
        for (const auto& index : shape.mesh.indices) {
            vertices.push_back(attrib.vertices[3 * index.vertex_index + 0]);
            vertices.push_back(attrib.vertices[3 * index.vertex_index + 1]);
            vertices.push_back(attrib.vertices[3 * index.vertex_index + 2]);

            if (index.texcoord_index >= 0) {
                vertices.push_back(attrib.texcoords[2 * index.texcoord_index + 0]);
                vertices.push_back(attrib.texcoords[2 * index.texcoord_index + 1]);
            } else {
                vertices.push_back(0.0f); vertices.push_back(0.0f);
            }

            if (index.normal_index >= 0) {
                vertices.push_back(attrib.normals[3 * index.normal_index + 0]);
                vertices.push_back(attrib.normals[3 * index.normal_index + 1]);
                vertices.push_back(attrib.normals[3 * index.normal_index + 2]);
            } else {
                vertices.push_back(0.0f); vertices.push_back(1.0f); vertices.push_back(0.0f);
            }
        }

        Mesh mesh;
        mesh.vertexCount = static_cast<int>(vertices.size() / 8);

        if (!shape.mesh.material_ids.empty() && shape.mesh.material_ids[0] >= 0) {
            int matID = shape.mesh.material_ids[0];
            mesh.textureID = materialTextures[materials[matID].name];
        } else {
            mesh.textureID = 0;
        }

        glGenVertexArrays(1, &mesh.VAO);
        glGenBuffers(1, &mesh.VBO);
        glBindVertexArray(mesh.VAO);
        glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
        glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
        glEnableVertexAttribArray(0);

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(3 * sizeof(float)));
        glEnableVertexAttribArray(1);

        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(5 * sizeof(float)));
        glEnableVertexAttribArray(2);
        
        sceneMeshes.push_back(mesh);
    }
    return true;
}

void updatePhys(float deltaTime) {
    if (!isGrounded) {
        velocityY += GRAVITY * deltaTime;
    }

    cameraPos[1] += velocityY * deltaTime;

    if (cameraPos[1] <= 0.0f) {
        cameraPos[1] = 0.0f;
        velocityY = 0.0f;
        isGrounded = true;
    }
}

void processInput(GLFWwindow *window) {
    static bool mPressed = false;
    static bool lPressed = false;

    if (glfwGetKey(window, GLFW_KEY_M) == GLFW_PRESS && !mPressed) {
        currentMode = EditMode::MODEL;
        std::cout << "Mode: PLACE MODELS" << std::endl;
        mPressed = true;
    } else if (glfwGetKey(window, GLFW_KEY_M) == GLFW_RELEASE) mPressed = false;

    if (glfwGetKey(window, GLFW_KEY_L) == GLFW_PRESS && !lPressed) {
        currentMode = EditMode::LIGHT;
        std::cout << "Mode: PLACE LIGHTS" << std::endl;
        lPressed = true;
    } else if (glfwGetKey(window, GLFW_KEY_L) == GLFW_RELEASE) lPressed = false;
    
    static bool iPressed = false;
    if (glfwGetKey(window, GLFW_KEY_I) == GLFW_PRESS) {
        if (!iPressed) {
            if (currentMode == EditMode::MODEL) {
                std::string path = openFilePicker();
                if (!path.empty()) {
                    clearCurrentModel();
                    if (loadModel(path)) {
                        currentModelPath = path;
                        isModelLoaded = true;
                        std::cout << "Successfully loaded: " << path << std::endl;
                    }
                }
            } else {
                std::cout << "Switch to MODEL mode to change the model!" << std::endl;
            }
            iPressed = true;
        }
    } else {
        iPressed = false;
    }

    float speed = cameraSpeed * deltaTime;

    glm::vec3 currentPos = glm::vec3(cameraPos[0], cameraPos[1], cameraPos[2]);
    glm::vec3 front = glm::normalize(glm::vec3(cameraFront.x, 0.0f, cameraFront.z));
    glm::vec3 right = glm::normalize(glm::cross(front, glm::vec3(0.0f, 1.0f, 0.0f)));

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);
    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
        currentPos += front * speed;
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
        currentPos -= front * speed;
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
        currentPos -= right * speed;
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
        currentPos += right * speed;

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS && isGrounded) {
        velocityY = 5.0f;
        isGrounded = false;
    }

    cameraPos[0] = currentPos.x;
    cameraPos[1] = currentPos.y;
    cameraPos[2] = currentPos.z;
}

void mouse_btn_callback(GLFWwindow* window, int button, int action, int mods) {
    if (button == GLFW_MOUSE_BUTTON_RIGHT && action == GLFW_PRESS) {

        float floorLevel = -1.0f;
        
        if (cameraFront.y < -0.01f) {
            float t = (floorLevel - cameraPos[1]) / cameraFront.y;
            
            glm::vec3 intersectPos;
            intersectPos.x = cameraPos[0] + t * cameraFront.x;
            intersectPos.y = floorLevel;
            intersectPos.z = cameraPos[2] + t * cameraFront.z;

            if (!sceneMeshes.empty()) {
                std::cout << "Object placed at: " << intersectPos.x << ", " << intersectPos.z << std::endl;
            }

            if (currentMode == EditMode::MODEL) {
                if (isModelLoaded) {
                    worldObjects.push_back({intersectPos, 0});
                    creationHistory.push_back({OBJ_MODEL});
                } else {
                    std::cout << "Model not assigned! Press I to load" << std::endl;
                }
            } else if (currentMode == EditMode::LIGHT) {
                worldLights.push_back({intersectPos + glm::vec3(0.0f, 3.0f, 0.0f)});
                creationHistory.push_back({OBJ_LIGHT});
                std::cout << "Light placed!" << std::endl;
            }
        }
    }
}

void mouse_callback(GLFWwindow* window, double xposIn, double yposIn) {
    float xpos = static_cast<float>(xposIn);
    float ypos = static_cast<float>(yposIn);

    if(firstMouse) {
        lastX = xpos;
        lastY = ypos;
        firstMouse = false;
    }

    float xoffset = xpos - lastX;
    float yoffset = lastY - ypos;
    lastX = xpos;
    lastY = ypos;

    float sensitivity = 0.1f;
    xoffset *= sensitivity;
    yoffset *= sensitivity;

    yaw += xoffset;
    pitch += yoffset;

    if (pitch > 89.0f) pitch = 89.0f;
    if (pitch < -89.0f) pitch = -89.0f;

    glm::vec3 front;
    front.x = cos(glm::radians(yaw)) * cos(glm::radians(pitch));
    front.y = sin(glm::radians(pitch));
    front.z = sin(glm::radians(yaw)) * cos(glm::radians(pitch));
    cameraFront = glm::normalize(front);
}

void renderScene(unsigned int shader, bool isFinalPass, unsigned int floorVAO) {
    unsigned int modelLoc = glGetUniformLocation(shader, "model");

    glUniform1i(glGetUniformLocation(shader, "isFloor"), 1);
    glm::mat4 model = glm::mat4(1.0f);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glBindVertexArray(floorVAO);
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4);

    glUniform1i(glGetUniformLocation(shader, "isFloor"), 0);
    for (const auto& obj : worldObjects) {
        model = glm::mat4(1.0f);
        model = glm::translate(model, obj.position);
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));

        for (const auto& currentMesh : sceneMeshes) {
            if (isFinalPass) {
                glActiveTexture(GL_TEXTURE0);
                glBindTexture(GL_TEXTURE_2D, currentMesh.textureID);
            }
            glBindVertexArray(currentMesh.VAO);
            glDrawArrays(GL_TRIANGLES, 0, currentMesh.vertexCount);
        }
    }
}

int main() {
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    glfwWindowHint(GLFW_SAMPLES, 4);

    GLFWwindow* window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "smol", NULL, NULL);
    if (window == NULL) {
        std::cerr << "Failed to create window" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwSetCursorPosCallback(window, mouse_callback);
    glfwSetMouseButtonCallback(window, mouse_btn_callback);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Failed to initialize GLAD" << std::endl;
        return -1;
    }

    glEnable(GL_MULTISAMPLE);
    glEnable(GL_DEPTH_TEST);

    std::string vShaderCode = readShaderCode("vertex.glsl");
    std::string fShaderCode = readShaderCode("fragment.glsl");
    std::string shShaderCode = readShaderCode("shadow_vertex.glsl");

    const char* vShaderPtr = vShaderCode.c_str();
    const char* fShaderPtr = fShaderCode.c_str();
    const char* shShaderPtr = shShaderCode.c_str();


    float planeVert[] = {
        // x,     y,      z,     u,    v,    nx,   ny,   nz
        -25.0f, -1.0f, -25.0f,  0.0f, 0.0f,  0.0f, 1.0f, 0.0f,
        25.0f, -1.0f, -25.0f,  1.0f, 0.0f,  0.0f, 1.0f, 0.0f,
        25.0f, -1.0f,  25.0f,  1.0f, 1.0f,  0.0f, 1.0f, 0.0f,
        -25.0f, -1.0f,  25.0f,  0.0f, 1.0f,  0.0f, 1.0f, 0.0f
    };

    unsigned int VBO, VAO;
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(planeVert), planeVert, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(5 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);

    if (!loadModel("/Users/kaffi/Downloads/spider-gwen-low-poly/source/model/model.obj")) {
        std::cout << "Model not found" << std::endl;
    }

    unsigned int vertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader, 1, &vShaderPtr, NULL);
    glCompileShader(vertexShader);

    unsigned int fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader, 1, &fShaderPtr, NULL);
    glCompileShader(fragmentShader);

    unsigned int shaderProgram = glCreateProgram();
    glAttachShader(shaderProgram, vertexShader);
    glAttachShader(shaderProgram, fragmentShader);
    glLinkProgram(shaderProgram);

    unsigned int shadowVertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(shadowVertexShader, 1, &shShaderPtr, NULL);
    glCompileShader(shadowVertexShader);

    unsigned int shadowProgram = glCreateProgram();
    glAttachShader(shadowProgram, shadowVertexShader);
    glLinkProgram(shadowProgram);

    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
    glDeleteShader(shadowVertexShader);

    const unsigned int SHADOW_WIDTH = 2048, SHADOW_HEIGHT = 2048;

    unsigned int depthMapFBO;
    glGenFramebuffers(1, &depthMapFBO);

    unsigned int depthMap;
    glGenTextures(1, &depthMap);
    glBindTexture(GL_TEXTURE_2D, depthMap);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
    float borderColor[] = { 1.0f, 1.0f, 1.0f, 1.0f };
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);

    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMap, 0);
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);

    while (!glfwWindowShouldClose(window)) {
        float currentFrame = glfwGetTime();
        deltaTime = currentFrame - lastFrame;
        lastFrame = currentFrame;

        processInput(window);

        updatePhys(deltaTime);

        if (glfwGetKey(window, GLFW_KEY_Z) == GLFW_PRESS) {
            if (!creationHistory.empty()) {
                HistoryItem last = creationHistory.back();
                if (last.type == OBJ_MODEL && !worldObjects.empty()) worldObjects.pop_back();
                if (last.type == OBJ_LIGHT && !worldLights.empty()) worldLights.pop_back();

                creationHistory.pop_back();
                std::this_thread::sleep_for(std::chrono::milliseconds(200));
            }
        }

        glClearColor(0.1f, 0.2f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glm::vec3 lightPos = (!worldLights.empty()) ? worldLights[0].position : glm::vec3(-2.0f, 10.0f, -1.0f);
        glm::mat4 lightProjection = glm::ortho(-20.0f, 20.0f, -20.0f, 20.0f, 1.0f, 50.f);
        glm::mat4 lightView = glm::lookAt(lightPos, glm::vec3(0.0f), glm::vec3(0.001f, 1.0f, 0.001f));
        glm::mat4 lightSpaceMatrix = lightProjection * lightView;

        glViewport(0, 0, 2048, 2048);
        glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
        glClear(GL_DEPTH_BUFFER_BIT);

        glUseProgram(shadowProgram);
        glUniformMatrix4fv(glGetUniformLocation(shadowProgram, "lightSpaceMatrix"), 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));
        renderScene(shadowProgram, false, VAO);

        glBindFramebuffer(GL_FRAMEBUFFER, 0);

        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glUseProgram(shaderProgram);

        glm::vec3 activeLightPos = (!worldLights.empty()) ? worldLights.back().position : glm::vec3(-2.0f, 10.0f, -1.0f);
        glm::mat4 projection = glm::perspective(glm::radians(45.0f), (float)SCR_WIDTH / SCR_HEIGHT, 0.1f, 100.0f);
        glm::mat4 view = glm::lookAt(glm::vec3(cameraPos[0], cameraPos[1], cameraPos[2]),
                                    glm::vec3(cameraPos[0], cameraPos[1], cameraPos[2]) + cameraFront,
                                    glm::vec3(0.0f, 1.0f, 0.0f));

        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "lightSpaceMatrix"), 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));
        glUniform3fv(glGetUniformLocation(shaderProgram, "viewPos"), 1, cameraPos);
        glUniform3fv(glGetUniformLocation(shaderProgram, "lightPos"), 1, glm::value_ptr(activeLightPos));

        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D, depthMap);
        glUniform1i(glGetUniformLocation(shaderProgram, "shadowMap"), 1);

        renderScene(shaderProgram, true, VAO);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}