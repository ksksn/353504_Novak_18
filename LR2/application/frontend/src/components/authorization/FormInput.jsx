import React, {useState} from "react";
import './jeneralStyles/textsStyles/ErrorText.css';

const FormInput = (props) => {
    const [focused, setFocused] = useState(false);
    const{ label, errorMessage, onChange, id, ...inputProps} = props;

    const handleFocus = (e) => {
        setFocused(true);
    }
    return(
        <div  className="errorText">
            <label> {label} </label>
            <input {...inputProps} 
            onChange = {onChange} 
            onBlur = {handleFocus} 
            focuced = {focused.toString()}/>
            <span> {errorMessage} </span>
        </div>
    )
}

export default FormInput