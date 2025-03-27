import React, { useState } from "react";
import Menu from "../menu/MainMenu";
import "../Grid.css";
import CodeInput from "./CodeTextArea"
import 'katex/dist/katex.min.css';
import Latex from "../../../../controllers/Latex";
import ContestService from "../../../../API/ContestService";
import { useParams } from "react-router-dom";

const Task = () => {
    const [properties, setProperties] = useState();
    const [file, setFile] = useState(null);
    const {id, problemId} = useParams();

    function setProblemProperties(problem_properties) {
        setProperties(problem_properties);
    }

    function NewlineText(props) {
        const text = props.text;
        const newText = text?.split('\n').map(str => <p>{str}</p>);
        
        return newText;
    }
      

    function showNotes() {
        if (!properties?.notes) {
            return <></>
        }
        return <>
                <p className="headline">Примечания</p>
                <Latex><NewlineText text = {properties.notes}/> </Latex>
                <p className="line"/>
            </>
    }

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        setFile(selectedFile);
      };

    async function submitSolution(){
        await ContestService.SubmitSolution({
            solution: file, 
            problemId: problemId,
            contestId: id
        })
        window.location.pathname=`/submissions/${problemId}`
    }

    return(
        <div className = "app-wrapper">
            <Menu setProblemProperties = {setProblemProperties}/>
            <div  className="content"> 
            
            <h1 className="contestsName">{properties?.name}</h1>
            <p className="limits"> 
                <Latex>Лимит времени: {properties?.timeLimit} мс </Latex><br/> 
                <Latex>Лимит памяти: {properties?.memoryLimit / 1024 / 1024} МБ </Latex>
            </p>
            <p className="line"/>
            <Latex> <NewlineText text = {properties?.legend}/></Latex>
            <p className="headline">Входные данные</p>
            <Latex><NewlineText text = {properties?.input}/></Latex>
            
            <p className="line"/>
            <p className="headline">Выходные данные</p>
            <Latex><NewlineText text = {properties?.output}/></Latex>

            <p className="line"/>
            {showNotes()}
            
            <p className="headline">Пример</p>
            <table>
                    <tr>
                        <td>STDIN </td>
                        <td>STDOUT </td>
                    </tr>
                    {properties?.sampleTests.map((sample, id) => (
                        <tr>
                            <td><Latex><NewlineText text = {sample.input}/></Latex></td>
                            <td><Latex><NewlineText text = {sample.output}/></Latex></td>
                        </tr>
                    ))}
            </table>
        
        <form method="post" enctype="multipart/form-data">
            <div style={{display:"flex", justifyContent:"left"}}>
                <input type="file" class="input-file" name="file" placeholder="Выберите файл" onChange={handleFileChange}/>
                <div style={{marginLeft:"15px;"}}>
                    <label className="compiler">Компилятор: </label>
                    <select>
                        <option value="C++17">GNU C++20</option>
                    </select>
                </div>
            </div>
            </form>
            <button className="sendButton"  type='submit' variant="contained" onClick={submitSolution}>
                        <p className="buttonText">Отправить </p>
                    </button>
            </div>
        </div>
    )
    
}


export default Task;