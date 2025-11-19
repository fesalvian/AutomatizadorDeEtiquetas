//mobile/EtiquetasApp/app/screens/ImageUploadScreen.tsx
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import axios from "axios";
import { router } from "expo-router";

export default function ImageUploadScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const backendUrl = "http://10.0.0.72:8000/upload-image"; // ⬅️ IP DO TEU PC

  async function pickFromGallery() {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  }

  useEffect(() => {
  (async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Permissão negada", "Você precisa liberar a câmera.");
    }
  })();
}, []);

  async function takePhoto() {
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  }

  async function enviarImagem() {
    if (!imageUri) {
      Alert.alert("Erro", "Selecione ou tire uma foto primeiro.");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", {
        uri: imageUri,
        name: "etiqueta.jpg",
        type: "image/jpeg",
      } as any);

      const response = await axios.post(backendUrl, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      Alert.alert("Sucesso", "Etiquetas extraídas e enviadas!");

      // opcional: voltar para tela inicial
      router.back();
    } catch (err) {
      console.log(err);
      Alert.alert("Erro", "Não foi possível enviar a imagem ao servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Enviar Foto das Etiquetas</Text>

      <View style={styles.previewBox}>
        {imageUri ? (
          <Image
            source={{ uri: imageUri }}
            style={{ width: "100%", height: "100%" }}
            resizeMode="contain"
          />
        ) : (
          <Text style={styles.previewText}>Nenhuma imagem selecionada</Text>
        )}
      </View>

      <TouchableOpacity style={styles.btn} onPress={pickFromGallery}>
        <Text style={styles.btnText}>Escolher da Galeria</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.btn} onPress={takePhoto}>
        <Text style={styles.btnText}>Tirar Foto</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.btnSend, loading && { opacity: 0.5 }]}
        onPress={enviarImagem}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Enviar Foto para IA</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 25,
    backgroundColor: "#f8fafc",
    flex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#2563eb",
    textAlign: "center",
    marginBottom: 20,
  },

  previewBox: {
    width: "100%",
    height: 280,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 12,
    backgroundColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  previewText: {
    color: "#94a3b8",
    fontSize: 16,
  },

  btn: {
    backgroundColor: "#1e3a8a",
    padding: 15,
    borderRadius: 10,
    marginBottom: 12,
  },
  btnSend: {
    backgroundColor: "#16a34a",
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  btnText: {
    color: "white",
    textAlign: "center",
    fontWeight: "bold",
    fontSize: 16,
  },
});
