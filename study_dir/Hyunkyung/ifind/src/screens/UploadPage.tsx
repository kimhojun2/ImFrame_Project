import AsyncStorage from "@react-native-async-storage/async-storage";
import firestore from '@react-native-firebase/firestore';
import storage from '@react-native-firebase/storage';
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import React, { useEffect, useState } from "react";
import { Alert, FlatList, Image, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import ImagePicker from 'react-native-image-crop-picker';
import { PERMISSIONS, RESULTS, request } from 'react-native-permissions';
import theme from "../styles/theme";

interface ImageInfo {
    uri: string;
    type?: string;
    name?: string | null;
    id: string | null;
    exif?: any;
}

interface UploadPageProps {
    navigation: NativeStackNavigationProp<any, 'MyPage'>;
}

//TODO : uuid 샘플 나중에 젯슨나노 키면 수정 필요!
// const serviceUUID = "12345678-1234-1234-1234-1234567890ab"; // 예시 UUID
// const characteristicUUID = "12345678-1234-1234-1234-1234567890cd"; // 예시 UUID
    
export const UploadPage = ({ navigation }: UploadPageProps) => {
    const [images, setImages] = useState<ImageInfo[]>([]);
    const [uploadButtonText, setUploadButtonText] = useState("사진 선택하기");
    

    //사진 폴더 접근 권한 요청
    useEffect(() => {
        requestPhotoPermission();
    }, []);

    const requestPhotoPermission = async () => {
        const status = await request(PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE); // 안드로이드 권한 요청
        if (status !== RESULTS.GRANTED) {
            Alert.alert('Permission Denied', 'We need permission to access your photos to upload.');
        }
    };

    const selectPhoto = () => {
        ImagePicker.openPicker({
            multiple: true,
            mediaType: "photo",
            includeExif: true,
            cropping: false,
            waitAnimationEnd: false,
            includeBase64: false,
        }).then(images => {
            const newImages = images.map((image) => ({
                uri: image.path,  // 이미지 경로
                type: image.mime,  // 이미지 MIME 타입
                name: image.filename || null,  // 파일 이름이 없는 경우 undefined
                id: image.filename || null,  // 고유 ID가 없는 경우 undefined
                exif: image.exif || {},  // EXIF 정보
            }));
    
            setImages(prevImages => [...prevImages, ...newImages]); // 기존 이미지 배열에 새 이미지 추가
        }).catch(e => {
            if (e.code === 'E_PICKER_CANCELLED') {
                console.log('사용자가 선택을 취소했습니다.');
            } else {
                console.error('이미지 선택 오류:', e);
            }
        });
    };
    
    
    const deleteImage = (id: string | null) => {
        if (id === null) {
            console.log("No ID provided, cannot delete image.");
            return;  // id가 null일 경우 함수 종료
        }
        const filteredImages = images.filter(image => image.id !== id);
        setImages(filteredImages);
    };
    
    const renderImageItem = ({ item }: { item: ImageInfo }) => {
        return (
            <View style={styles.imageContainer}>
                <Image source={{ uri: item.uri }} style={styles.imagePreview} />
                <TouchableOpacity
                    style={styles.deleteButton}
                    onPress={() => deleteImage(item.id)}
                >
                    <Text style={styles.deleteButtonText}>X</Text>
                </TouchableOpacity>
            </View>
        );
    };
    
    const handleUploadImages = async () => {
        if (images.length < 1) {
            Alert.alert("사진을 선택해주세요!");
            return;
        }
    
        const uid = await AsyncStorage.getItem('userUID');
        if (!uid) {
            Alert.alert("사용자 인증 오류", "사용자 정보를 찾을 수 없습니다.");
            return;
        }
    
        const uploadedUrls = [];
        for (let img of images) {
            const uploadUri = img.uri;
            let filename = img.uri.substring(img.uri.lastIndexOf('/') + 1);
            const extension = filename.split('.').pop();
            const name = filename.split('.').slice(0, -1).join('.');
            filename = `${name}_${Date.now()}.${extension}`;
    
            const storageRef = storage().ref(`users/${uid}/${filename}`);
            try {
                await storageRef.putFile(uploadUri, {
                    customMetadata: {
                        // 메타데이터 필드 추가
                        type: img.type || '',
                        name: img.name || '',
                        exif: JSON.stringify(img.exif)  // EXIF 정보는 문자열로 변환하여 저장
                    }
                });
                const url = await storageRef.getDownloadURL();
                uploadedUrls.push(url);
            } catch (e) {
                console.error('업로드 실패:', e);
            }
        }
    
        // Firestore에 URL 배열 저장
        try {
            await firestore().collection('users').doc(uid).update({
                images: firestore.FieldValue.arrayUnion(...uploadedUrls)
            });
            Alert.alert("업로드 완료", "모든 이미지가 성공적으로 업로드되었습니다.");
            setImages([]);
        } catch (error) {
            console.error('Firestore 저장 오류:', error);
            Alert.alert("업로드 실패", "이미지 저장에 실패했습니다.");
        }
    
        // try {
        //     // 블루투스 모듈 초기화
        //     await BleManager.start({ showAlert: false });
    
        //     // 10초간 스캔 시작
        //     await BleManager.scan([], 10, true);
        //     console.log('Scanning...');
    
        //     setTimeout(async () => {
        //         // 스캔된 장치 확인
        //         const peripherals = await BleManager.getDiscoveredPeripherals();
        //         if (peripherals.length === 0) {
        //             console.log('No peripherals found');
        //         } else {
        //             console.log('Found peripherals:', peripherals);
    
        //             // 장치 연결 로직 (첫 번째 검색된 장치에 연결 예정)
        //             let targetPeripheral = peripherals[0];
        //             await BleManager.connect(targetPeripheral.id);
        //             console.log('Connected to ' + targetPeripheral.id);
    
        //             // 이미지 전송 로직
        //             for (const image of images) {
        //                 let imageBase64 = await FileSystem.readAsStringAsync(image.uri, { encoding: 'base64' });
        //                 let bytes = base64.toByteArray(imageBase64);
        //                 let numberArray = Array.from(bytes); // Uint8Array를 number[]로 변환
        //                 await BleManager.write(targetPeripheral.id, serviceUUID, characteristicUUID, numberArray);
        //                 console.log('Image sent');
        //             }
        //         }
        //     }, 5000);
        // } catch (error) {
        //     console.log('Error:', error);
        // }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>사진 업로드</Text>
                <View style={styles.separator} />
                <FlatList
                    data={images}
                    renderItem={renderImageItem}
                    keyExtractor={(item, index) => item.id || item.uri || index.toString()}
                    numColumns={3}
                    contentContainerStyle={styles.imageList}
                />
            <View style={styles.buttonContainer}>
                <TouchableOpacity style={styles.select_button} onPress={selectPhoto}>
                    <Text style={styles.buttonText}>{'선택'}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.select_button} onPress={handleUploadImages}>
                    <Text style={styles.buttonText}>{'전송'}</Text>
                </TouchableOpacity>
            </View>
        </View>
    )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        backgroundColor: '#fff',
    },
    title:{
        paddingTop: 10,
        margin: 10,
        fontSize: 35,
        // fontWeight: "bold",
        color: theme.mainDarkGrey,
        fontFamily: theme.mainfont,
    },
    separator: {
        width: '90%',
        height: 1,
        backgroundColor: theme.navicolor,
        marginBottom: 5,
    },
    imageList: {
        // alignItems: 'center',
        // justifyContent: 'center',
    },
    imageContainer: {
        position: 'relative',
        margin: 5,
    },
    imagePreview: {
        width: 100,
        height: 100,
    },
    deleteButton: {
        position: 'absolute',
        top: 0,
        right: 0,
        backgroundColor: theme.mainRed,
        borderRadius: 15,
        paddingLeft: 10,
        paddingRight: 10,
        paddingTop: 5,
        paddingBottom : 5,
    },
    deleteButtonText: {
        color: 'white',
        fontSize: 14,
    },
    buttonContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        width: '100%',
        padding: 30,
    },
    select_button: {
        // marginBottom: 30,
        paddingTop: 10,
        paddingBottom: 10,
        width: '30%',
        alignItems: 'center',
        backgroundColor: theme.mainOrange,
        borderRadius: 40,
    },
    buttonText: {
        fontFamily: theme.mainfont,
        padding: 5,
        color: 'black',
        fontSize: 23,
    },
    });