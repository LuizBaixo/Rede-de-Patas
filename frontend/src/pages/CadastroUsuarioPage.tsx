import { useState } from "react";
import axios from "axios";
import InputMask from "react-input-mask";
import { Eye, EyeOff } from "lucide-react";

export default function CadastroUsuarioPage() {
  const [form, setForm] = useState({
    nome: "",
    email: "",
    telefone: "",
    endereco_cep: "",
    endereco_completo: "",
    moradia: "",
    telas_em_casa: false,
    criancas_em_casa: false,
    area_aberta: false,
    possui_animais: false,
    tipo_animais: "",
    qtde_animais: 0,
    is_admin: false,
    senha: ""
  });

  const [mostrarSenha, setMostrarSenha] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));

    if (name === "endereco_cep" && value.replace(/\D/g, "").length === 8) {
      buscarEnderecoPorCEP(value);
    }
  };

  const buscarEnderecoPorCEP = async (cep: string) => {
    try {
      const res = await axios.get(`https://viacep.com.br/ws/${cep}/json/`);
      if (!res.data.erro) {
        const { logradouro, bairro, localidade, uf } = res.data;
        const enderecoCompleto = `${logradouro}, ${bairro} - ${localidade}/${uf}`;
        setForm((prev) => ({
          ...prev,
          endereco_completo: enderecoCompleto
        }));
      }
    } catch (error) {
      console.error("Erro ao buscar CEP:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/usuarios/", form);
      alert("Usuário cadastrado com sucesso!");
      console.log(response.data);
    } catch (error) {
      alert("Erro ao cadastrar.");
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="max-w-xl w-full space-y-4">
        <h1 className="text-2xl font-bold mb-4 text-center">Cadastro de Usuário</h1>

        <input name="nome" placeholder="Nome" className="w-full p-2 bg-gray-800 rounded" onChange={handleChange} required />
        <input name="email" placeholder="Email" type="email" className="w-full p-2 bg-gray-800 rounded" onChange={handleChange} required />

        <InputMask
          mask="(99) 99999-9999"
          value={form.telefone}
          onChange={handleChange}
        >
          {(inputProps: any) => (
            <input
              {...inputProps}
              name="telefone"
              placeholder="Telefone"
              className="w-full p-2 bg-gray-800 rounded"
              required
            />
          )}
        </InputMask>

        <input name="endereco_cep" placeholder="CEP" maxLength={8} className="w-full p-2 bg-gray-800 rounded" onChange={handleChange} required />
        <input name="endereco_completo" value={form.endereco_completo} readOnly className="w-full p-2 bg-gray-700 rounded" />

        <input name="moradia" placeholder="Tipo de moradia" className="w-full p-2 bg-gray-800 rounded" onChange={handleChange} />
        <input name="tipo_animais" placeholder="Tipo de animais" className="w-full p-2 bg-gray-800 rounded" onChange={handleChange} />
        <input name="qtde_animais" placeholder="Quantidade de animais" type="number" className="w-full p-2 bg-gray-800 rounded" onChange={handleChange} />

        <div className="flex gap-4 flex-wrap">
          <label><input type="checkbox" name="telas_em_casa" onChange={handleChange} /> Telas em casa</label>
          <label><input type="checkbox" name="criancas_em_casa" onChange={handleChange} /> Crianças em casa</label>
          <label><input type="checkbox" name="area_aberta" onChange={handleChange} /> Área aberta</label>
          <label><input type="checkbox" name="possui_animais" onChange={handleChange} /> Possui outros animais</label>
          <label><input type="checkbox" name="is_admin" onChange={handleChange} /> É administrador</label>
        </div>

        <div className="relative">
          <input
            name="senha"
            type={mostrarSenha ? "text" : "password"}
            placeholder="Senha"
            className="w-full p-2 bg-gray-800 rounded pr-10"
            onChange={handleChange}
            required
          />
          <button
            type="button"
            onClick={() => setMostrarSenha(!mostrarSenha)}
            className="absolute right-2 top-2 text-gray-400 hover:text-white"
          >
            {mostrarSenha ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        </div>

        <button type="submit" className="bg-blue-600 hover:bg-blue-700 w-full py-2 rounded font-semibold">
          Cadastrar
        </button>
      </form>
    </div>
  );
}
