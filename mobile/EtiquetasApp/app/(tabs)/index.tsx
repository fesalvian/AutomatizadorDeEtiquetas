import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { router } from "expo-router";

export default function Home() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Automatizador de Etiquetas</Text>

      <TouchableOpacity
        style={styles.btn}
        onPress={() => router.push("/screens/ManualFormScreen")}
      >
        <Text style={styles.btnText}>Criar etiqueta manual</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.btn}
        onPress={() => router.push("/screens/ImageUploadScreen")}
      >
        <Text style={styles.btnText}>Enviar imagem para IA</Text>
      </TouchableOpacity>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
    justifyContent: "center",
    padding: 20
  },
  title: {
    fontSize: 26,
    fontWeight: "bold",
    marginBottom: 40,
    textAlign: "center",
    color: "#2563eb"
  },
  btn: {
    backgroundColor: "#2563eb",
    padding: 16,
    borderRadius: 10,
    marginBottom: 20
  },
  btnText: {
    textAlign: "center",
    color: "white",
    fontSize: 16,
    fontWeight: "bold"
  }
});
