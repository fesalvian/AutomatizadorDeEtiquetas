//mobile/EtiquetasApp/app/screens/ManualFormScreen.tsx
import React, { useState, useCallback, useEffect } from "react";
import { useFocusEffect } from "@react-navigation/native";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
} from "react-native";
import axios from "axios";
import { router } from "expo-router";

const SERVER = "http://10.0.0.72:8000";

export default function ManualFormScreen() {
  const [comodo, setComodo] = useState("");
  const [peca, setPeca] = useState("");
  const [medida1, setMedida1] = useState("");
  const [medida2, setMedida2] = useState("");
  const [quantidade, setQuantidade] = useState("");
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [lista, setLista] = useState<any[]>([]);


 // ---- BUSCAR LISTA DO SERVIDOR ----
const fetchLista = async () => {
  try {
    const res = await axios.get(`${SERVER}/labels`);

    // força re-render (deep clone)
    const novaLista = JSON.parse(JSON.stringify(res.data));

    // atualiza SOMENTE se mudou
    if (JSON.stringify(novaLista) !== JSON.stringify(lista)) {
      setLista(novaLista);
    }

  } catch (err) {
    console.log("Erro ao buscar lista", err);
  }
};

// Ao entrar na tela
useFocusEffect(
  useCallback(() => {
    fetchLista();
  }, [])
);

// Atualização automática
useEffect(() => {
  const interval = setInterval(fetchLista, 1000);
  return () => clearInterval(interval);
}, []);


  // Atualiza depois de enviar
  const refresh = () => fetchLista();

  const enviar = async () => {
  if (!comodo || !peca || !medida1 || !medida2 || !quantidade) {
    Alert.alert("Campos incompletos", "Preencha tudo antes de enviar.");
    return;
  }

  const payload = {
    comodo,
    peca,
    medida1,
    medida2,
    quantidade,
  };

  try {
    try {
  if (editIndex === null) {
    await axios.post(`${SERVER}/add-label`, payload);
    Alert.alert("Criado!", "Etiqueta adicionada.");
  } else {
    await axios.put(`${SERVER}/edit/${editIndex}`, payload);
    Alert.alert("Editado!", "Etiqueta atualizada.");
  }
} catch (err: any) {
  console.log("ERRO AO ENVIAR:", err?.response?.data || err);
  Alert.alert("Erro", "Não foi possível enviar/editar.");
}

// sempre sair do modo edição
setEditIndex(null);

    // limpa
    setComodo("");
    setPeca("");
    setMedida1("");
    setMedida2("");
    setQuantidade("");

    refresh();
  } catch (err) {
    Alert.alert("Erro", "Não foi possível enviar/editar.");
  }
};

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Criar Etiqueta Manual</Text>

      {editIndex !== null && (
  <View style={{
    backgroundColor: "#fef3c7",
    borderLeftWidth: 4,
    borderLeftColor: "#f59e0b",
    padding: 10,
    borderRadius: 8,
    marginBottom: 12
  }}>
    <Text style={{ color: "#92400e", fontWeight: "700" }}>
      Editando etiqueta #{editIndex + 1}
    </Text>
  </View>
)}


      <Text style={styles.label}>Cômodo</Text>
      <TextInput
        style={styles.input}
        value={comodo}
        onChangeText={setComodo}
        placeholder="Ex: Banheiro"
      />

      <Text style={styles.label}>Peça</Text>
      <TextInput
        style={styles.input}
        value={peca}
        onChangeText={setPeca}
        placeholder="Ex: Porta toalha"
      />

      <Text style={styles.label}>Medida (0000 x 0000)</Text>
      <View style={styles.medidaRow}>
        <TextInput
          style={[styles.input, styles.medidaInput]}
          keyboardType="numeric"
          maxLength={4}
          value={medida1}
          onChangeText={setMedida1}
        />
        <Text style={styles.x}>x</Text>
        <TextInput
          style={[styles.input, styles.medidaInput]}
          keyboardType="numeric"
          maxLength={4}
          value={medida2}
          onChangeText={setMedida2}
        />
      </View>

      <Text style={styles.label}>Quantidade</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={quantidade}
        onChangeText={setQuantidade}
        placeholder="Ex: 5"
      />

      <TouchableOpacity style={styles.btn} onPress={enviar}>
        <Text style={styles.btnText}>Enviar Etiqueta</Text>
      </TouchableOpacity>

      {/* LISTA DE ETIQUETAS ENVIADAS */}
<Text style={styles.subtitle}>Etiquetas enviadas</Text>

<View style={styles.listBox}>
  {lista.map((item, i) => (
    <View key={i} style={styles.itemRowContainer}>
      <View style={{ flex: 1 }}>
        <Text style={styles.itemText}>
          {item.comodo} | {item.peca} | {item.medida1} x {item.medida2} | x{item.quantidade}
        </Text>
      </View>

      {/* BOTÃO EDITAR */}
      <TouchableOpacity
  style={styles.editBtn}
  onPress={() => {
    setEditIndex(item.id);
    setComodo(item.comodo);
    setPeca(item.peca);
    setMedida1(item.medida1);
    setMedida2(item.medida2);
    setQuantidade(String(item.quantidade));
  }}
>
  <Text style={styles.editText}>Editar</Text>
</TouchableOpacity>


      {/* BOTÃO EXCLUIR */}
      <TouchableOpacity
  style={styles.delBtn}
  onPress={() => {
    Alert.alert("Excluir?", "Tem certeza?", [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Excluir",
        style: "destructive",
        onPress: async () => {
          await axios.delete(`${SERVER}/delete/${item.id}`);
          refresh();
        },
      },
    ]);
  }}
>
  <Text style={styles.delText}>X</Text>
</TouchableOpacity>

    </View>
  ))}
</View>

{/* BOTÃO LIMPAR TUDO */}
<TouchableOpacity
  style={styles.clearAllBtn}
  onPress={() => {
    Alert.alert(
      "Limpar tudo?",
      "Isso removerá TODAS as etiquetas. Tem certeza?",
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Sim, limpar tudo",
          style: "destructive",
          onPress: async () => {
            await axios.delete(`${SERVER}/clear`);
            refresh();
          },
        },
      ]
    );
  }}
>
  <Text style={styles.clearAllText}>Limpar Tudo</Text>
</TouchableOpacity>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: "#f8fafc",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#2563eb",
    marginBottom: 20,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 20,
    fontWeight: "600",
    color: "#1e293b",
    marginTop: 35,
    marginBottom: 10,
  },
  listBox: {
    backgroundColor: "white",
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#cbd5e1",
  },
  item: {
    paddingVertical: 6,
  },
  itemText: {
    fontSize: 15,
    color: "#1e293b",
  },
  label: {
    fontSize: 16,
    fontWeight: "600",
    marginTop: 15,
    marginBottom: 5,
    color: "#1e293b",
  },
  input: {
    backgroundColor: "white",
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    fontSize: 16,
  },
  medidaRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  medidaInput: {
    width: "40%",
  },
  x: {
    marginHorizontal: 12,
    fontSize: 20,
    fontWeight: "bold",
    color: "#1e293b",
  },
  btn: {
    backgroundColor: "#2563eb",
    padding: 15,
    marginTop: 30,
    borderRadius: 10,
  },
  btnText: {
    color: "white",
    fontSize: 17,
    fontWeight: "bold",
    textAlign: "center",
  },
  itemRow: {
  flexDirection: "row",
  alignItems: "center",
  paddingVertical: 6,
},
itemRowContainer: {
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "space-between",
  padding: 10,
  backgroundColor: "#fff",
  borderRadius: 10,
  marginBottom: 8,
  borderWidth: 1,
  borderColor: "#e2e8f0",
},

editBtn: {
  backgroundColor: "#facc15",
  paddingHorizontal: 10,
  paddingVertical: 4,
  borderRadius: 6,
  marginRight: 8,
},

editText: {
  color: "#1e293b",
  fontWeight: "600",
},

delBtn: {
  backgroundColor: "#ef4444",
  paddingHorizontal: 10,
  paddingVertical: 4,
  borderRadius: 6,
},

delText: {
  color: "white",
  fontWeight: "bold",
},

clearAllBtn: {
  backgroundColor: "#dc2626",
  padding: 12,
  borderRadius: 10,
  marginTop: 20,
},

clearAllText: {
  textAlign: "center",
  fontSize: 16,
  color: "white",
  fontWeight: "bold",
},

});
